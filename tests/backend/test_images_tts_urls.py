import base64
import io
import socket

import pytest
from PIL import Image, PngImagePlugin

from backend.errors import RpcError
from backend.images import Images
from backend.storage import DEFAULTS
from backend.transport import Response, Transport, check_response, resolve, validate_address, validate_endpoint
from backend.tts import TTS
from conftest import FakeTransport
from test_service import configured, finish, request


def synthetic_image(format="PNG", size=(1600, 900)):
    output = io.BytesIO()
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Private", "must-be-removed")
    Image.new("RGB", size, "navy").save(output, format=format,
                                        **({"pnginfo": metadata} if format == "PNG" else {}))
    return base64.b64encode(output.getvalue()).decode("ascii")


@pytest.mark.parametrize("format,mime", [("PNG", "image/png"), ("JPEG", "image/jpeg")])
def test_images_strip_resize_bound_approval_and_single_use(clock, format, mime):
    images = Images(clock)
    destination = {"provider": "openai", "model": "configured-model", "endpoint": "cloud"}
    prepared = images.prepare(synthetic_image(format), mime, "session", destination)
    assert prepared["width"] == 1280 and prepared["height"] == 720
    with Image.open(io.BytesIO(base64.b64decode(prepared["preview"].split(",")[1]))) as result:
        assert not result.getexif() and "Private" not in result.info
    with pytest.raises(RpcError):
        images.take(prepared["imageRef"], "session", destination)
    with pytest.raises(RpcError):
        images.approve(prepared["imageRef"], "other-session", destination)
    with pytest.raises(RpcError):
        images.approve(prepared["imageRef"], "session", {**destination, "model": "other"})
    images.approve(prepared["imageRef"], "session", destination)
    sent = images.take(prepared["imageRef"], "session", destination)
    assert sent["mime"] == "image/jpeg"
    with pytest.raises(RpcError):
        images.take(prepared["imageRef"], "session", destination)
    new = images.prepare(synthetic_image(), "image/png", "session", destination)
    clock.now = 301
    with pytest.raises(RpcError):
        images.approve(new["imageRef"], "session", destination)
    assert not images.items


@pytest.mark.parametrize("data,mime", [("not-base64", "image/png"),
    (base64.b64encode(b"secret non-image file").decode(), "image/png"),
    (base64.b64encode(b'<svg onload="alert(1)"></svg>').decode(), "image/svg+xml"),
    ("a" * 7_000_001, "image/png"), (synthetic_image(), "image/jpeg"),
    (synthetic_image(size=(5000, 4001)), "image/png")],
    ids=["invalid-base64", "non-image", "svg", "too-large", "wrong-mime", "too-many-pixels"])
def test_bad_images(clock, data, mime):
    with pytest.raises(RpcError):
        Images(clock).prepare(data, mime, "session", {})


async def test_image_rpc_revocation_provider_change_and_no_path(tmp_path, clock, transport):
    service, _ = await configured(tmp_path, clock, transport)
    args = {"dataBase64": synthetic_image(), "mime": "image/png", "sessionId": service.context["sessionId"]}
    assert (await service.rpc("prepare_image", args))["error"]["code"] == "CONSENT_REQUIRED"
    await service.rpc("update_settings", {"imagesEnabled": True, "visionConfirmed": True})
    assert (await service.rpc("prepare_image", {"path": "../../secrets.json"}))["error"]["code"] == "INVALID_INPUT"
    prepared = (await service.rpc("prepare_image", args))["data"]
    await service.rpc("approve_image_send", {"imageRef": prepared["imageRef"],
        "sessionId": service.context["sessionId"], "destination": prepared["destination"]})
    await service.rpc("start_assistant_request", request(service, imageRef=prepared["imageRef"]))
    await finish(service)
    assert transport.calls[-1]["body"]["messages"][-1]["images"]
    assert not service.images.items
    prepared = (await service.rpc("prepare_image", args))["data"]
    await service.rpc("update_settings", {"provider": "gemini"})
    assert not service.images.items
    assert (await service.rpc("approve_image_send", {"imageRef": prepared["imageRef"],
        "sessionId": service.context["sessionId"], "destination": prepared["destination"]}))["error"]["code"] == "CONSENT_REQUIRED"
    await service.close()


@pytest.mark.parametrize("endpoint", ["file:///etc/passwd", "ftp://localhost", "http://user:pass@localhost",
    "http://169.254.169.254", "http://[fe80::1]", "http://[::ffff:169.254.169.254]",
    "http://[::]", "http://localhost/api/chat", "http://localhost?key=secret", "http://localhost#x",
    "http://127.0.0.1:0", "http://host%20name", "http://[fe80::1%eth0]", "http://100.100.100.200"])
def test_ssrf_endpoint_rejections(endpoint):
    with pytest.raises(RpcError):
        validate_endpoint(endpoint)


@pytest.mark.parametrize("endpoint", ["http://127.0.0.1:11434", "http://192.168.0.15:11434",
    "https://ollama.example.org", "http://[::1]:11434"])
def test_explicit_lan_and_loopback_allowed(endpoint):
    assert validate_endpoint(endpoint) == endpoint


def test_dns_revalidation_and_mixed_answers(monkeypatch):
    def addresses(host, port, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.0.15", port)),
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.169.254", port))]
    monkeypatch.setattr(socket, "getaddrinfo", addresses)
    with pytest.raises(RpcError):
        resolve("example.org", 11434, private=True)
    assert validate_address("192.168.0.15", private=True) == "192.168.0.15"
    with pytest.raises(RpcError):
        validate_address("192.168.0.15")


async def test_transport_offline_guard_and_cloud_host_fixed():
    transport = Transport()
    with pytest.raises(RpcError):
        await transport.request("https://evil.example/v1/responses", {}, {})
    with pytest.raises(AssertionError, match="forbids"):
        await transport.request("https://api.openai.com/v1/responses", {}, {})
    await transport.close()


def test_http_errors_do_not_parse_sensitive_payload():
    with pytest.raises(RpcError) as caught:
        check_response(Response(429, {"retry-after": "bad value"}, b"PRIVATE_API_KEY"))
    assert caught.value.retry_after_ms == 90000 and "PRIVATE_API_KEY" not in str(caught.value)


async def test_remote_tts_consent_no_implicit_fallback_and_audio():
    audio = b"RIFF" + b"0000" + b"WAVE" + b"synthetic audio"
    transport = FakeTransport(audio)
    tts = TTS(transport, executable="")
    assert not tts.capabilities()["local"]
    with pytest.raises(RpcError) as caught:
        await tts.synthesize("text", DEFAULTS, {})
    assert caught.value.code == "VOICE_UNAVAILABLE" and not transport.calls
    settings = {**DEFAULTS, "ttsEngine": "openai"}
    with pytest.raises(RpcError) as caught:
        await tts.synthesize("private answer", settings, {"openai": "synthetic-key"})
    assert caught.value.code == "CONSENT_REQUIRED" and not transport.calls
    settings["ttsConsent"] = True
    result = await tts.synthesize("t" * 2000, settings, {"openai": "synthetic-key"})
    assert result["mime"] == "audio/wav"
    assert base64.b64decode(result["audioBase64"]) == audio
    call = transport.calls[0]
    assert call["url"].endswith("/v1/audio/speech")
    assert len(call["body"]["input"]) == 1000 and call["body"]["voice"] == "coral"


async def test_local_tts_uses_stdin_safe_argv_and_stop():
    captured = {}

    class Input:
        def write(self, data):
            captured["stdin"] = data

        async def drain(self):
            pass

        def close(self):
            pass

    class Output:
        done = False

        async def read(self, count):
            if self.done:
                return b""
            self.done = True
            return b"RIFF0000WAVEsynthetic"

    class Process:
        stdin = Input()
        stdout = Output()
        returncode = None

        async def wait(self):
            self.returncode = 0
            return 0

        def kill(self):
            captured["killed"] = True
            self.returncode = -9

    async def spawn(*args, **kwargs):
        captured["argv"] = args
        return Process()
    tts = TTS(FakeTransport(), executable="/usr/bin/espeak-ng", spawn=spawn)
    await tts.synthesize("$(touch /tmp/injection); & secret", DEFAULTS, {})
    assert captured["argv"] == ("/usr/bin/espeak-ng", "-v", "it", "--stdout", "--stdin")
    assert captured["stdin"] == b"$(touch /tmp/injection); & secret"
    assert tts.process is None
    tts.process = Process()
    tts.process.returncode = None
    await tts.stop()
    assert captured["killed"]
