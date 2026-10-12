import base64
import http.client
import socket
from urllib.parse import urlsplit

import pytest

from backend.errors import RpcError
from backend.transport import Transport
from test_images_tts_urls import synthetic_image
from test_service import configured

REAL_REQUEST = Transport._request


@pytest.mark.parametrize("status,body,limit,code", [(301, b"redirect", 100, "NETWORK_ERROR"),
    (200, b"x" * 101, 100, "NETWORK_ERROR"), (429, b"secret", 100, "RATE_LIMITED"),
    (200, b"safe", 100, None)])
async def test_real_transport_pins_socket_limits_and_rejects_redirects(monkeypatch, status, body, limit, code):
    observed = {}

    class Socket:
        def __init__(self, *args):
            pass

        def settimeout(self, seconds):
            observed["timeout"] = seconds

        def connect(self, address):
            observed["address"] = address

        def close(self):
            pass

    class Response:
        def __init__(self):
            self.status = status
            self.remaining = body

        def getheaders(self):
            return [("location", "http://169.254.169.254/"), ("retry-after", "12")]

        def read1(self, size):
            chunk, self.remaining = self.remaining[:size], self.remaining[size:]
            return chunk

    class Connection:
        def __init__(self, host, port, timeout):
            observed["host"] = host

        def request(self, method, path, body, headers):
            observed["headers"] = headers

        def getresponse(self):
            return Response()

        def close(self):
            self.sock.close()

    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.0.15", 11434))])
    # Mock only the real synchronous HTTP worker; asyncio's internal sockets remain real.
    transport = Transport()
    import threading
    with monkeypatch.context() as patch:
        patch.setattr(socket, "socket", Socket)
        patch.setattr(http.client, "HTTPConnection", Connection)
        if code:
            with pytest.raises(RpcError) as caught:
                REAL_REQUEST(transport, urlsplit("http://ollama.example:11434/api/chat"), {}, b"{}",
                             True, 45, limit, "POST", threading.Event(), [])
            assert caught.value.code == code
        else:
            result = REAL_REQUEST(transport, urlsplit("http://ollama.example:11434/api/chat"), {}, b"{}",
                                  True, 45, limit, "POST", threading.Event(), [])
            assert result.body == b"safe"
    assert observed["address"] == ("192.168.0.15", 11434)
    assert observed["host"] == "ollama.example"
    assert not transport.connections


async def test_scoped_file_import_rejects_traversal_secret_and_fake_image(tmp_path, clock, transport):
    service, _ = await configured(tmp_path, clock, transport)
    await service.rpc("update_settings", {"imagesEnabled": True})
    root = service.import_store.root
    (root / "selected.png").write_bytes(base64.b64decode(synthetic_image()))
    if root.joinpath("selected.png").exists():
        # Files copied by the user may have public mode; source import is not secret storage.
        result = await service.rpc("prepare_import_image", {"filename": "selected.png", "sessionId": service.context["sessionId"]})
        assert result["ok"] and result["data"]["width"] == 1280
    for filename in ("../secrets.json", "C:\\private.png", "/etc/private.png", "secrets.json"):
        result = await service.rpc("prepare_import_image", {"filename": filename, "sessionId": service.context["sessionId"]})
        assert result["error"]["code"] == "INVALID_INPUT"
    (root / "fake.png").write_bytes(b"PRIVATE SECRET TEXT")
    result = await service.rpc("prepare_import_image", {"filename": "fake.png", "sessionId": service.context["sessionId"]})
    assert result["error"]["code"] == "INVALID_INPUT"
    assert "PRIVATE" not in str(result)
    await service.close()


async def test_import_symlink_denied(tmp_path, clock, transport):
    service, _ = await configured(tmp_path, clock, transport)
    await service.rpc("update_settings", {"imagesEnabled": True})
    target = tmp_path / "outside.png"
    target.write_bytes(base64.b64decode(synthetic_image()))
    link = service.import_store.root / "link.png"
    try:
        link.symlink_to(target)
    except OSError:
        await service.close()
        pytest.skip("Windows symlink privilege unavailable; Linux CI covers this")
    result = await service.rpc("prepare_import_image", {"filename": "link.png", "sessionId": service.context["sessionId"]})
    assert result["error"]["code"] == "STORAGE_ERROR"
    await service.close()
