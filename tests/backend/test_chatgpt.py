import asyncio
import json
import time
from urllib.parse import parse_qs, urlsplit

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from backend.chatgpt_auth import ChatGPTAuth, ISSUER, PLAN_SCOPE
from backend.errors import RpcError
from backend.providers import ChatGPT
from backend.storage import DEFAULTS, PrivateStore
from backend.transport import Response


class OAuthTransport:
    def __init__(self):
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.calls = []
        self.claims = {}
        self.scope = PLAN_SCOPE
        self.bad_signature = False
        self.fail_refresh = False
        self.fail_revoke = False

    async def request(self, url, headers, body=None, **kwargs):
        self.calls.append((url, headers, body))
        if url.endswith("openid-configuration"):
            data = {
                "issuer": ISSUER,
                "jwks_uri": ISSUER + "/keys",
                "revocation_endpoint": ISSUER + "/revoke",
            }
        elif url.endswith("/keys"):
            key = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(self.key.public_key()))
            data = {"keys": [{**key, "kid": "synthetic-key", "alg": "RS256"}]}
        elif url.endswith("/revoke"):
            if self.fail_revoke:
                raise RpcError("NETWORK_ERROR")
            return Response(200, {}, b"")
        else:
            form = parse_qs(body.decode())
            refresh = form["grant_type"] == ["refresh_token"]
            if refresh and self.fail_refresh:
                raise RpcError("UNAUTHORIZED")
            key = (
                rsa.generate_private_key(public_exponent=65537, key_size=2048)
                if self.bad_signature
                else self.key
            )
            data = {
                "token_type": "Bearer",
                "access_token": "synthetic-access",
                "refresh_token": "rotated-refresh" if refresh else "synthetic-refresh",
                "expires_in": 3600,
                "scope": self.scope,
            }
            if not refresh:
                data["id_token"] = jwt.encode(
                    self.claims, key, algorithm="RS256", headers={"kid": "synthetic-key"}
                )
        return Response(200, {}, json.dumps(data).encode())


async def attempt(tmp_path, monkeypatch):
    class Server:
        sockets = [type("Socket", (), {"getsockname": lambda self: ("127.0.0.1", 14555)})()]

        def close(self):
            pass

        async def wait_closed(self):
            pass

    async def listener(callback, host, port, **kwargs):
        assert host == "127.0.0.1" and port == 0
        return Server()

    monkeypatch.setattr(asyncio, "start_server", listener)
    transport = OAuthTransport()
    auth = ChatGPTAuth(PrivateStore(tmp_path), transport)
    url = (await auth.begin())["authorizationUrl"]
    params = parse_qs(urlsplit(url).query)
    now = int(time.time())
    transport.claims = {
        "iss": ISSUER,
        "aud": "issued-client",
        "sub": "synthetic-account",
        "iat": now,
        "exp": now + 3600,
        "nonce": auth.pending["nonce"],
    }
    callback = {
        "state": auth.pending["state"],
        "code": "synthetic-code",
        "client_id": "issued-client",
    }
    return auth, transport, params, callback


async def test_pkce_issued_client_private_storage_and_reauthorization(tmp_path, monkeypatch):
    auth, transport, query, callback = await attempt(tmp_path, monkeypatch)
    verifier = auth.pending["verifier"]
    assert query["client_id"] == ["dynamic_agent_client"] and query["agent_name_hint"] == [
        "Decky Pilot"
    ]
    assert query["code_challenge_method"] == ["S256"] and "code_verifier" not in query
    await auth.complete(callback)
    assert auth.public()["connected"] and "access_token" not in str(auth.public())
    token_call = next(call for call in transport.calls if call[0].endswith("/token"))
    form = parse_qs(token_call[2].decode())
    assert form["client_id"] == ["issued-client"] and form["code_verifier"] == [verifier]
    assert form["redirect_uri"] == query["redirect_uri"] and "client_secret" not in form
    with pytest.raises(RpcError):
        await auth.complete(callback)
    host = auth.data["host"]
    await auth.begin(auth.data["active"])
    assert auth.pending["client_id"] == "issued-client" and auth.data["host"] == host
    await auth.close()


@pytest.mark.parametrize(
    "invalid",
    [
        "state",
        "nonce",
        "issuer",
        "audience",
        "expiry",
        "signature",
        "client",
        "permission",
        "denial",
    ],
)
async def test_reject_invalid_auth_without_overwriting_active_account(
    tmp_path, monkeypatch, invalid
):
    auth, transport, _, callback = await attempt(tmp_path, monkeypatch)
    if invalid == "state":
        callback["state"] = "wrong"
    elif invalid == "nonce":
        transport.claims["nonce"] = "wrong"
    elif invalid == "issuer":
        transport.claims["iss"] = "https://invalid.example"
    elif invalid == "audience":
        transport.claims["aud"] = "wrong"
    elif invalid == "expiry":
        transport.claims["exp"] = int(time.time()) - 60
    elif invalid == "signature":
        transport.bad_signature = True
    elif invalid == "client":
        callback.pop("client_id")
    elif invalid == "permission":
        transport.scope = "openid email"
    elif invalid == "denial":
        callback["error"] = "access_denied"
    with pytest.raises(RpcError):
        await auth.complete(callback)
    assert not auth.public()["connected"] and not auth.data["accounts"]
    if invalid in ("state", "client", "denial"):
        assert not any(call[0].endswith("/token") for call in transport.calls)
    await auth.close()


async def test_refresh_serialized_rotation_and_unconfirmed_revocation(tmp_path, monkeypatch):
    auth, transport, _, callback = await attempt(tmp_path, monkeypatch)
    await auth.complete(callback)
    auth.data["accounts"][auth.data["active"]]["expires_at"] = 0
    tokens = await asyncio.gather(auth.access_token(), auth.access_token())
    assert tokens == ["synthetic-access"] * 2
    assert sum(b"grant_type=refresh_token" in (c[2] or b"") for c in transport.calls) == 1
    assert auth.data["accounts"][auth.data["active"]]["refresh_token"] == "rotated-refresh"
    transport.fail_revoke = True
    assert not (await auth.disconnect())["revocationConfirmed"]
    assert auth.public()["error"] == "REVOCATION_UNCONFIRMED" and not auth.public()["connected"]
    record = auth.data["accounts"][auth.data["active"]]
    assert record["client_id"] == "issued-client" and "refresh_token" not in record
    await auth.close()


async def test_failed_refresh_requires_reauthorization(tmp_path, monkeypatch):
    auth, transport, _, callback = await attempt(tmp_path, monkeypatch)
    await auth.complete(callback)
    auth.data["accounts"][auth.data["active"]]["expires_at"] = 0
    transport.fail_refresh = True
    with pytest.raises(RpcError) as error:
        await auth.access_token()
    assert error.value.code == "AUTH_EXPIRED"
    await auth.close()


async def test_returning_client_mismatch_preserves_verified_registration(tmp_path, monkeypatch):
    auth, transport, _, callback = await attempt(tmp_path, monkeypatch)
    await auth.complete(callback)
    original = json.loads(json.dumps(auth.data))
    await auth.begin(auth.data["active"])
    callback = {"state": auth.pending["state"], "code": "synthetic", "client_id": "different-client"}
    with pytest.raises(RpcError):
        await auth.complete(callback)
    assert auth.data == original and auth.public()["connected"]
    await auth.close()


@pytest.mark.parametrize(
    "ending,code",
    [
        ("completed", None),
        ("incomplete", "PROVIDER_BLOCKED"),
        ("failed", "PLAN_LIMIT"),
        ("missing", "NETWORK_ERROR"),
    ],
)
async def test_plan_sse_terminal_and_preview_fields(ending, code):
    data = {
        "type": "response." + ending,
        "response": {
            "status": ending,
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "Synthetic advice"}],
                }
            ],
            "error": {"code": "subscription_sharing_usage_limit_exceeded"},
        },
    }

    class Stream:
        async def request(self, url, headers, body, **kwargs):
            assert url == "https://api.openai.com/v1/responses"
            assert body["stream"] is True and body["store"] is False
            assert "max_output_tokens" not in body and "previous_response_id" not in body
            return Response(200, {}, ("data: " + json.dumps(data) + "\n\n").encode())

    provider = ChatGPT(Stream())
    settings = {**DEFAULTS, "model": "returned-slug", "remoteConsent": True}
    if code:
        with pytest.raises(RpcError) as error:
            await provider.generate(
                settings,
                {"chatgpt": "synthetic-token"},
                "policy",
                [{"role": "user", "content": "help"}],
            )
        assert error.value.code == code
    else:
        result = await provider.generate(
            settings,
            {"chatgpt": "synthetic-token"},
            "policy",
            [{"role": "user", "content": "help"}],
        )
        assert result["answer"] == "Synthetic advice"
