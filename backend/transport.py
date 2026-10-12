"""Bounded stdlib HTTP. DNS is validated and pinned for each socket; no redirects/proxies."""
import asyncio
import http.client
import ipaddress
import json
import socket
import ssl
import threading
import time
from dataclasses import dataclass
from urllib.parse import parse_qs, urlsplit

from .errors import RpcError, require, string

CLOUD_HOSTS = {"api.openai.com", "auth.openai.com", "api.x.ai",
               "generativelanguage.googleapis.com", "api.anthropic.com"}


def validate_endpoint(endpoint):
    string(endpoint, 500, 1)
    try:
        url = urlsplit(endpoint)
        require(url.scheme in ("http", "https") and bool(url.hostname))
        require(not url.username and not url.password and not url.query and not url.fragment)
        require(not url.path.strip("/") and not any(c in endpoint for c in "\\\r\n\t %"))
        require(url.port is None or 1 <= url.port <= 65535)
        host = url.hostname
        require(host is not None and "%" not in host)
        try:
            validate_address(host, private=True)
        except ValueError:
            require(all(c.isalnum() or c in ".-" for c in host))
        return endpoint.rstrip("/")
    except ValueError as exc:
        raise RpcError("INVALID_INPUT") from exc


def validate_address(address, private=False):
    ip = ipaddress.ip_address(address)
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    require(not (ip.is_link_local or ip.is_multicast or ip.is_unspecified or
                 ip.is_reserved and not ip.is_loopback),
            "INVALID_INPUT")
    # Metadata, CGNAT and IPv6 translation mechanisms are outside the Ollama LAN scope.
    if isinstance(ip, ipaddress.IPv4Address):
        require(ip not in ipaddress.ip_network("100.64.0.0/10"), "INVALID_INPUT")
    else:
        require(ip not in ipaddress.ip_network("64:ff9b::/96") and
                ip not in ipaddress.ip_network("2002::/16") and
                ip not in ipaddress.ip_network("2001::/32"), "INVALID_INPUT")
    require(private or ip.is_global, "INVALID_INPUT")
    return str(ip)


def resolve(host, port, private=False):
    try:
        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise RpcError("NETWORK_ERROR") from exc
    require(bool(addresses), "NETWORK_ERROR")
    # Reject mixed safe/unsafe answers rather than selecting only one safe address.
    for _, _, _, _, target in addresses:
        validate_address(target[0], private)
    return addresses


@dataclass
class Response:
    status: int
    headers: dict
    body: bytes

    def json(self):
        try:
            value = json.loads(self.body)
            require(isinstance(value, dict), "NETWORK_ERROR")
            return value
        except (ValueError, UnicodeError) as exc:
            raise RpcError("NETWORK_ERROR") from exc


def check_response(response):
    if 200 <= response.status < 300:
        return response
    code = {401: "AUTH_FAILED", 403: "AUTH_FAILED", 404: "MODEL_UNAVAILABLE",
            429: "RATE_LIMITED", 400: "INVALID_INPUT"}.get(response.status, "NETWORK_ERROR")
    retry = None
    if response.status == 429:
        value = response.headers.get("retry-after", "90")
        try:
            retry = min(3_600_000, max(1000, int(float(value) * 1000)))
        except (ValueError, TypeError, OverflowError):
            retry = 90_000
    raise RpcError(code, retry)


class Transport:
    def __init__(self):
        self.closed = False
        self.connections = set()
        self.guard = threading.Lock()

    async def request(self, url, headers, body=None, *, private=False, deadline=45,
                      limit=2_000_000, method="POST"):
        require(not self.closed, "CANCELLED")
        parsed = urlsplit(url)
        require(parsed.hostname and not parsed.username and not parsed.password and not parsed.fragment)
        if parsed.query:
            permitted = {("api.anthropic.com", "/v1/models"): "after_id",
                         ("generativelanguage.googleapis.com", "/v1beta/models"): "pageToken"}
            key = permitted.get((parsed.hostname, parsed.path))
            query = parse_qs(parsed.query, strict_parsing=True)
            require(method == "GET" and key and set(query) == {key} and len(query[key]) == 1 and
                    0 < len(query[key][0]) <= 2000)
        if private:
            validate_endpoint(f"{parsed.scheme}://{parsed.netloc}")
        else:
            require(parsed.scheme == "https" and parsed.hostname in CLOUD_HOSTS)
        cancelled = threading.Event()
        holder = []
        payload = body if isinstance(body, bytes) else None if body is None else json.dumps(body).encode("utf-8")
        try:
            async with asyncio.timeout(deadline):
                return await asyncio.to_thread(self._request, parsed, headers, payload, private,
                                               deadline, limit, method, cancelled, holder)
        except TimeoutError as exc:
            raise RpcError("TIMEOUT") from exc
        finally:
            cancelled.set()
            for connection in holder:
                connection.close()

    def _request(self, parsed, headers, payload, private, deadline, limit, method,
                 cancelled, holder):
        end = time.monotonic() + deadline
        connection = None
        try:
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            addresses = resolve(host, port, private)
            require(not cancelled.is_set() and not self.closed, "CANCELLED")
            connection = http.client.HTTPConnection(host, port, timeout=5)
            holder.append(connection)
            with self.guard:
                self.connections.add(connection)
            last_error = None
            for family, socktype, protocol, _, address in addresses:
                require(not cancelled.is_set(), "CANCELLED")
                sock = socket.socket(family, socktype, protocol)
                sock.settimeout(min(5, max(0.1, end - time.monotonic())))
                connection.sock = sock
                try:
                    sock.connect(address)
                    if parsed.scheme == "https":
                        connection.sock = ssl.create_default_context().wrap_socket(
                            sock, server_hostname=host)
                    break
                except OSError as exc:
                    sock.close()
                    last_error = exc
            else:
                raise RpcError("NETWORK_ERROR") from last_error
            require(not cancelled.is_set(), "CANCELLED")
            connection.sock.settimeout(max(0.1, end - time.monotonic()))
            connection.request(method, (parsed.path or "/") + ("?" + parsed.query if parsed.query else ""), body=payload,
                               headers={"Content-Type": "application/json", "Accept": "*/*",
                                        "Connection": "close", **headers})
            response = connection.getresponse()
            # Redirects never follow, including cross-host redirects carrying authentication.
            require(not 300 <= response.status < 400, "NETWORK_ERROR")
            result = bytearray()
            while True:
                require(not cancelled.is_set() and time.monotonic() < end, "TIMEOUT")
                connection.sock.settimeout(max(0.1, end - time.monotonic()))
                chunk = response.read1(min(65536, limit + 1 - len(result)))
                if not chunk:
                    break
                result.extend(chunk)
                require(len(result) <= limit, "NETWORK_ERROR")
            return check_response(Response(response.status,
                {k.lower(): v for k, v in response.getheaders()}, bytes(result)))
        except (TimeoutError, socket.timeout) as exc:
            raise RpcError("TIMEOUT") from exc
        except (OSError, http.client.HTTPException) as exc:
            raise RpcError("NETWORK_ERROR") from exc
        finally:
            if connection:
                connection.close()
                with self.guard:
                    self.connections.discard(connection)

    async def close(self):
        self.closed = True
        with self.guard:
            for connection in self.connections:
                connection.close()
