import json
import socket

import pytest

from backend.transport import Response, Transport, check_response


class FakeTransport:
    def __init__(self, data=None, status=200, error=None):
        self.data = data if data is not None else {"message": {"content": "Open the blue door."},
                                                   "capabilities": ["completion", "vision"]}
        self.status, self.error = status, error
        self.calls = []
        self.closed = False

    async def request(self, url, headers, body=None, **kwargs):
        self.calls.append({"url": url, "headers": headers, "body": body, **kwargs})
        if self.error:
            raise self.error
        payload = self.data if isinstance(self.data, bytes) else json.dumps(self.data).encode()
        return check_response(Response(self.status, {"retry-after": "12"}, payload))

    async def close(self):
        self.closed = True


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline suite forbids DNS/network egress")
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    # Windows asyncio itself uses TCP loopback for socketpair. Block the production
    # transport entry point and DNS, leaving only asyncio's internal wakeup pipe.
    monkeypatch.setattr(Transport, "_request", forbidden)


@pytest.fixture
def clock():
    class Clock:
        now = 0

        def __call__(self):
            return self.now
    return Clock()


@pytest.fixture
def transport():
    return FakeTransport()
