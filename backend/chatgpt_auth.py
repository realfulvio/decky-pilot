"""OpenAI OSS public-client OAuth. Own loopback listener and credentials only."""
import asyncio
import base64
import hashlib
import hmac
import secrets
import time
import uuid
from urllib.parse import parse_qs, urlencode, urlsplit

import jwt

from .errors import RpcError, require, string
from .transport import check_response

ISSUER = "https://auth.openai.com"
RESOURCE = "https://api.openai.com/v1"
TOKEN = ISSUER + "/api/accounts/oauth/token"
PLAN_SCOPE = "chatgpt.tokens.use.direct"


class ChatGPTAuth:
    def __init__(self, store, transport, clock=time.time):
        self.store, self.transport, self.clock = store, transport, clock
        self.data = store.read("chatgpt-auth.json", {"host": "urn:uuid:" + str(uuid.uuid4()),
                                                 "active": None, "accounts": {}})
        require(isinstance(self.data, dict) and isinstance(self.data.get("accounts"), dict), "STORAGE_ERROR")
        self.pending = self.server = self.timer = None
        self.state = "idle"
        self.error = None
        self.lock = asyncio.Lock()
        self.handlers = set()
        self.on_change = None
        self.on_connected = None
        self.epoch = 0

    def save(self):
        self.store.write("chatgpt-auth.json", self.data)

    def public(self):
        account = self.data["accounts"].get(self.data["active"], {})
        return {"state": self.state, "error": self.error, "active": self.data["active"],
                "connected": bool(account.get("access_token") and PLAN_SCOPE in account.get("scopes", []) and self.error != "AUTH_EXPIRED"),
                "accounts": [{"id": key, "label": value.get("email") or "ChatGPT account",
                              "registration": index + 1} for index, (key, value) in
                             enumerate(self.data["accounts"].items())]}

    async def begin(self, account_id=None):
        await self.cancel()
        require(account_id is None or account_id in self.data["accounts"])
        account = self.data["accounts"].get(account_id, {})
        verifier = secrets.token_urlsafe(48)
        self.server = await asyncio.start_server(self.handle, "127.0.0.1", 0, limit=8192)
        port = self.server.sockets[0].getsockname()[1]
        self.pending = {"state": secrets.token_urlsafe(32), "nonce": secrets.token_urlsafe(32),
                        "verifier": verifier, "redirect_uri": f"http://127.0.0.1:{port}/auth/callback",
                        "client_id": account.get("client_id", "dynamic_agent_client"),
                        "account": account_id, "expires": self.clock() + 300}
        query = {"client_id": self.pending["client_id"], "ext_agent_host_id": self.data["host"],
                 "response_type": "code", "redirect_uri": self.pending["redirect_uri"],
                 "scope": "openid profile email offline_access resource.invoke " + PLAN_SCOPE,
                 "resource": RESOURCE, "state": self.pending["state"], "nonce": self.pending["nonce"],
                 "code_challenge_method": "S256", "code_challenge": base64.urlsafe_b64encode(
                     hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")}
        if not account_id:
            query["agent_name_hint"] = "Decky Pilot"
        elif account.get("id_token"):
            query["id_token_hint"] = account["id_token"]
        self.save()
        self.state, self.error = "pending", None
        self.timer = asyncio.create_task(self.expire())
        return {"authorizationUrl": ISSUER + "/api/accounts/authorize?" + urlencode(query)}

    async def expire(self):
        await asyncio.sleep(300)
        await self.cancel()
        self.state, self.error = "error", "AUTH_EXPIRED"

    async def cancel(self):
        self.epoch += 1
        self.pending = None
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        if self.timer and self.timer is not asyncio.current_task():
            self.timer.cancel()
            await asyncio.gather(self.timer, return_exceptions=True)
        self.timer = None

    async def handle(self, reader, writer):
        task = asyncio.current_task()
        self.handlers.add(task)
        success = False
        try:
            request = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 5)
            require(len(request) <= 8192)
            method, target, _ = request.split(b"\r\n", 1)[0].decode("ascii").split(" ", 2)
            parsed = urlsplit(target)
            require(method == "GET" and parsed.path == "/auth/callback" and not parsed.netloc)
            pairs = parse_qs(parsed.query, strict_parsing=True)
            require(all(len(v) == 1 for v in pairs.values()))
            await self.complete({k: v[0] for k, v in pairs.items()})
            success = True
        except Exception:
            pass  # Never log callback URLs, codes, tokens, or provider bodies.
        finally:
            body = b"Decky Pilot: connected. Return to the app." if success else b"Decky Pilot: sign-in not completed. Return to the app."
            try:
                writer.write(b"HTTP/1.1 " + (b"200 OK" if success else b"400 Bad Request") +
                             b"\r\nContent-Type: text/plain\r\nCache-Control: no-store\r\nConnection: close\r\nContent-Length: " +
                             str(len(body)).encode() + b"\r\n\r\n" + body)
                await writer.drain()
            finally:
                writer.close()
                self.handlers.discard(task)

    async def json(self, url):
        return check_response(await self.transport.request(url, {}, method="GET")).json()

    async def form(self, url, body):
        response = await self.transport.request(url, {"Content-Type": "application/x-www-form-urlencoded"},
                                                urlencode(body).encode())
        return check_response(response)

    async def verify(self, token, client_id, nonce):
        discovery = await self.json(ISSUER + "/.well-known/openid-configuration")
        require(discovery.get("issuer") == ISSUER, "AUTH_INVALID")
        uri = discovery.get("jwks_uri", "")
        require(uri.startswith(ISSUER + "/"), "AUTH_INVALID")
        jwks = await self.json(uri)
        try:
            header = jwt.get_unverified_header(token)
            require(header.get("alg") == "RS256", "AUTH_INVALID")
            key = next(k for k in jwks["keys"] if k.get("kid") == header.get("kid") and
                       k.get("kty") == "RSA" and k.get("use", "sig") == "sig")
            claims = jwt.decode(token, jwt.PyJWK.from_dict(key, algorithm="RS256").key,
                                algorithms=["RS256"], audience=client_id, issuer=ISSUER,
                                leeway=5, options={"require": ["sub", "exp", "iat", "nonce"]})
            require(isinstance(claims["nonce"], str) and hmac.compare_digest(claims["nonce"], nonce) and
                    isinstance(claims["sub"], str) and bool(claims["sub"]), "AUTH_INVALID")
            return claims
        except (jwt.PyJWTError, KeyError, StopIteration, TypeError, ValueError) as exc:
            raise RpcError("AUTH_INVALID") from exc

    def credential(self, tokens, base):
        require(tokens.get("token_type", "").lower() == "bearer", "AUTH_INVALID")
        access = string(tokens.get("access_token"), 20000, 1)
        scopes = tokens.get("scope", " ".join(base.get("scopes", []))).split()
        require(PLAN_SCOPE in scopes, "PLAN_PERMISSION_REQUIRED")
        expiry = tokens.get("expires_in")
        require(type(expiry) is int and 0 < expiry <= 86400, "AUTH_INVALID")
        refresh = string(tokens.get("refresh_token", base.get("refresh_token")), 20000, 1)
        return {**base, "access_token": access, "refresh_token": refresh,
                "id_token": tokens.get("id_token", base.get("id_token")),
                "scopes": scopes, "expires_at": self.clock() + expiry}

    async def complete(self, values):
        pending = self.pending
        require(pending and self.clock() < pending["expires"], "AUTH_EXPIRED")
        require(isinstance(values.get("state"), str) and
                hmac.compare_digest(values["state"], pending["state"]), "AUTH_INVALID")
        await self.cancel()  # Consume the attempt once, before exchanging anything.
        epoch = self.epoch
        try:
            require(not values.get("error"), "AUTH_DENIED")
            client = values.get("client_id", pending["client_id"])
            require(client != "dynamic_agent_client" and isinstance(client, str) and
                    1 <= len(client) <= 200, "AUTH_INVALID")
            require(pending["client_id"] == "dynamic_agent_client" or client == pending["client_id"], "AUTH_INVALID")
            code = string(values.get("code"), 4096, 1)
            tokens = (await self.form(TOKEN, {"grant_type": "authorization_code", "client_id": client,
                "code": code, "code_verifier": pending["verifier"], "redirect_uri": pending["redirect_uri"],
                "resource": RESOURCE})).json()
            claims = await self.verify(tokens.get("id_token"), client, pending["nonce"])
            previous = self.data["accounts"].get(pending["account"], {})
            require(not previous or claims["sub"] == previous["subject"], "AUTH_INVALID")
            record = self.credential(tokens, {"client_id": client, "subject": claims["sub"],
                "email": claims.get("email", ""), "scopes": []})
            account_id = hashlib.sha256((client + ":" + claims["sub"]).encode()).hexdigest()[:24]
            require(self.epoch == epoch, "AUTH_INVALID")
            if self.on_change:
                await self.on_change()
            async with self.lock:
                require(self.epoch == epoch, "AUTH_INVALID")
                self.data["accounts"][account_id] = record
                self.data["active"] = account_id
                self.save()
            self.state, self.error = "connected", None
            if self.on_connected:
                await self.on_connected()
        except Exception as exc:
            self.state, self.error = "error", exc.code if isinstance(exc, RpcError) else "AUTH_INVALID"
            raise

    async def access_token(self):
        async with self.lock:
            account = self.data["accounts"].get(self.data["active"])
            require(account and account.get("access_token"), "NOT_CONFIGURED")
            require(PLAN_SCOPE in account.get("scopes", []), "PLAN_PERMISSION_REQUIRED")
            if self.clock() >= account["expires_at"] - 60:
                try:
                    tokens = (await self.form(TOKEN, {"grant_type": "refresh_token", "client_id": account["client_id"],
                        "refresh_token": account["refresh_token"], "resource": RESOURCE})).json()
                    updated = self.credential(tokens, account)
                    self.data["accounts"][self.data["active"]] = updated
                    self.save()
                    account = updated
                except Exception as exc:
                    self.state, self.error = "error", "AUTH_EXPIRED"
                    raise RpcError("AUTH_EXPIRED") from exc
            return account["access_token"]

    async def disconnect(self):
        await self.cancel()
        async with self.lock:
            account = self.data["accounts"].get(self.data["active"], {})
            revoked = not bool(account.get("refresh_token"))
            try:
                if not revoked:
                    discovery = await self.json(ISSUER + "/.well-known/openid-configuration")
                    endpoint = discovery.get("revocation_endpoint", "")
                    require(endpoint.startswith(ISSUER + "/"), "AUTH_INVALID")
                    response = await self.form(endpoint, {"token": account["refresh_token"],
                        "token_type_hint": "refresh_token", "client_id": account["client_id"]})
                    revoked = response.status == 200
            except Exception:
                revoked = False
            for name in ("access_token", "refresh_token", "id_token", "expires_at", "scopes"):
                account.pop(name, None)
            self.save()
            self.state, self.error = "idle", None if revoked else "REVOCATION_UNCONFIRMED"
            return {"revocationConfirmed": revoked}

    async def close(self):
        await self.cancel()
        tasks = [task for task in self.handlers if task is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
