"""Exercise the registry probe over a synthetic Unix server, never a compositor.

These tests establish the probe's bounded, read-only wire contract, not pixel safety.
"""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import json
import socket
import struct
import sys
import threading

import pytest

from scripts.probe_capture_protocols import REQUIRED, probe

pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="Linux peer credentials")


def event(object_id, opcode, body):
    return struct.pack("=II", object_id, ((8 + len(body)) << 16) | opcode) + body


def global_event(name, interface, version=1):
    value = interface.encode() + b"\0"
    return event(2, 0, struct.pack("=II", name, len(value)) + value
                 + b"\0" * (-len(value) % 4) + struct.pack("=I", version))


DONE = event(3, 0, struct.pack("=I", 99))


@contextmanager
def server(tmp_path, response, *, fragment=False, stalled=False):
    path = tmp_path / "wayland-test"
    stopped = threading.Event()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
        listener.bind(str(path))
        listener.listen(1)
        listener.settimeout(2)

        def serve():
            with listener.accept()[0] as connection:
                connection.settimeout(2)
                requests = b""
                while len(requests) < 24:
                    data = connection.recv(24 - len(requests))
                    assert data, "Probe disconnected before registry/sync"
                    requests += data
                # Independent literal wire contract. No registry.bind or capture request.
                assert struct.unpack("=6I", requests) == (1, 786433, 2, 1, 786432, 3)
                if fragment:
                    for byte in response:
                        connection.sendall(bytes([byte]))
                else:
                    connection.sendall(response)
                if stalled:
                    stopped.wait(1)
                else:
                    connection.shutdown(socket.SHUT_WR)
                try:
                    extra = connection.recv(1024)
                except ConnectionResetError:
                    extra = b""  # Client may reject an invalid header before reading its body.
                assert extra == b"", "Unexpected request after registry/sync"

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(serve)
            try:
                yield path
            finally:
                stopped.set()
                future.result(timeout=3)


def test_candidate_advertisement_never_validates_capture(tmp_path):
    response = b"".join(global_event(i + 10, name) for i, name in enumerate(REQUIRED))
    response += global_event(20, "private_test_label_do_not_log") + DONE
    with server(tmp_path, response, fragment=True) as path:
        report = probe(path)
    assert report["status"] == "candidate_advertised"
    assert report["capture_safety_validated"] is False
    assert report["missing"] == []
    assert report["protocols"] == dict.fromkeys(REQUIRED, 1)
    assert "private_test_label" not in json.dumps(report)


def test_output_capture_is_not_a_toplevel_candidate(tmp_path):
    response = global_event(5, "gamescope_pipewire")
    response += global_event(6, "ext_output_image_capture_source_manager_v1") + DONE
    with server(tmp_path, response) as path:
        report = probe(path)
    assert report["status"] == "unsupported"
    assert report["missing"] == list(REQUIRED)


def test_removed_global_is_not_available(tmp_path):
    response = b"".join(global_event(i + 10, name) for i, name in enumerate(REQUIRED))
    response += event(2, 1, struct.pack("=I", 11)) + DONE
    with server(tmp_path, response) as path:
        report = probe(path)
    assert report["status"] == "unsupported"
    assert report["missing"] == [REQUIRED[1]]


@pytest.mark.parametrize(("response", "reason"), [
    (event(1, 0, struct.pack("=III", 1, 1, 21)
           + b"private server error\0\0\0\0"), "compositor_error"),
    (struct.pack("=II", 2, 4 << 16), "invalid_message"),
    (event(2, 0, struct.pack("=III", 4, 9000, 1)), "invalid_global"),
    (event(9, 0, b""), "unexpected_event"),
    (global_event(8, REQUIRED[0], 0), "invalid_global"),
    (global_event(8, REQUIRED[0]) * 2, "invalid_global"),
    (b"", "disconnected"),
])
def test_failure_discards_partial_capabilities_and_server_text(tmp_path, response, reason):
    with server(tmp_path, global_event(42, REQUIRED[2]) + response) as path:
        report = probe(path)
    assert report["status"] == "unavailable"
    assert report["reason"] == reason
    assert report["protocols"] == {}
    assert "private server error" not in json.dumps(report)


def test_stalled_server_has_deadline(tmp_path):
    with server(tmp_path, global_event(42, REQUIRED[2]), stalled=True) as path:
        report = probe(path, timeout=0.05)
    assert report["reason"] == "timeout"
    assert report["protocols"] == {}


def test_missing_socket(tmp_path):
    assert probe(tmp_path / "absent")["reason"] == "socket_unavailable"


def test_symlink_socket_rejected_before_connect(tmp_path):
    path = tmp_path / "actual"
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
        listener.bind(str(path))
        alias = tmp_path / "alias"
        alias.symlink_to(path)
        assert probe(alias)["reason"] == "absolute_nonsymlink_socket_required"


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), 31])
def test_invalid_deadline_never_connects(tmp_path, timeout):
    assert probe(tmp_path / "absent", timeout)["reason"] == "invalid_timeout"
