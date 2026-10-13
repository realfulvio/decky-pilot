"""Opt-in Linux Wayland registry probe: no bind, windows, pixels, or provider imports.

Only wl_display.get_registry and wl_display.sync are sent. Presence is NOT safety
validation. The plugin never imports this development tool; packaging excludes scripts.
"""

import argparse
import json
import math
import os
from pathlib import Path
import socket
import stat
import struct
import sys
import time


REQUIRED = (
    "ext_foreign_toplevel_list_v1",
    "ext_foreign_toplevel_image_capture_source_manager_v1",
    "ext_image_copy_capture_manager_v1",
)
KNOWN = (*REQUIRED, "gamescope_control", "gamescope_pipewire",
         "zwlr_screencopy_manager_v1", "ext_output_image_capture_source_manager_v1")
MAX_BYTES = 262144


class ProbeError(Exception):
    """Fixed, non-sensitive diagnostic code (never include server error text)."""


def _receive(connection, count, deadline):
    data = bytearray()
    while len(data) < count:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError
        connection.settimeout(remaining)
        part = connection.recv(count - len(data))
        if not part:
            raise ProbeError("disconnected")
        data.extend(part)
    return bytes(data)


def _registry(connection, deadline):
    # wl_display id=1: get_registry(new_id=2), sync(new_id=3).
    # Never bind any advertised global, even when a candidate is present.
    connection.sendall(struct.pack("=III", 1, (12 << 16) | 1, 2)
                       + struct.pack("=III", 1, 12 << 16, 3))
    globals_by_id = {}
    total = 0
    while total < MAX_BYTES:
        object_id, header = struct.unpack("=II", _receive(connection, 8, deadline))
        size, opcode = header >> 16, header & 0xFFFF
        if size < 8 or size % 4 or total + size > MAX_BYTES:
            raise ProbeError("invalid_message")
        body = _receive(connection, size - 8, deadline)
        total += size
        if object_id == 1 and opcode == 0:
            raise ProbeError("compositor_error")
        if object_id == 3 and opcode == 0 and len(body) == 4:
            return globals_by_id
        if object_id == 2 and opcode == 0 and len(body) >= 12:
            name, length = struct.unpack_from("=II", body)
            padded = (length + 3) & ~3
            if not 1 <= length <= 256 or len(body) != 12 + padded:
                raise ProbeError("invalid_global")
            value = body[8:8 + length]
            if value[-1:] != b"\0" or b"\0" in value[:-1]:
                raise ProbeError("invalid_global")
            try:
                interface = value[:-1].decode("ascii")
            except UnicodeDecodeError:
                raise ProbeError("invalid_global") from None
            version, = struct.unpack_from("=I", body, 8 + padded)
            if version == 0 or name in globals_by_id:
                raise ProbeError("invalid_global")
            globals_by_id[name] = (interface if interface in KNOWN else None, version)
        elif object_id == 2 and opcode == 1 and len(body) == 4:
            name, = struct.unpack("=I", body)
            globals_by_id.pop(name, None)
        else:
            raise ProbeError("unexpected_event")
    raise ProbeError("response_limit")


def probe(path, timeout=3.0):
    """Return allowlisted capabilities; every failure discards partial discoveries."""
    report = {"schema": 1, "status": "unavailable", "protocols": {},
              "missing": list(REQUIRED), "capture_safety_validated": False}
    try:
        if not math.isfinite(timeout) or not 0 < timeout <= 30:
            raise ProbeError("invalid_timeout")
        if sys.platform != "linux":
            raise ProbeError("linux_required")
        path = Path(path)
        if not path.is_absolute() or path.resolve() != path:
            raise ProbeError("absolute_nonsymlink_socket_required")
        info = path.lstat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid():
            raise ProbeError("socket_not_owned")
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            deadline = time.monotonic() + timeout
            connection.settimeout(timeout)
            connection.connect(str(path))
            _, peer_uid, _ = struct.unpack("=3i", connection.getsockopt(
                socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("=3i")))
            if peer_uid != os.getuid():
                raise ProbeError("peer_not_owned")
            registry = _registry(connection, deadline)
        protocols = {}
        for interface, version in registry.values():
            if interface is not None:
                protocols[interface] = max(protocols.get(interface, 0), version)
        report["protocols"] = dict(sorted(protocols.items()))
        report["missing"] = [name for name in REQUIRED if name not in protocols]
        report["status"] = "candidate_advertised" if not report["missing"] else "unsupported"
    except ProbeError as error:
        report["reason"] = str(error)
    except TimeoutError:
        report["reason"] = "timeout"
    except OSError:
        report["reason"] = "socket_unavailable"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True, type=Path,
                        help="Explicit absolute Wayland socket owned by this Linux user")
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args()
    report = probe(args.socket, args.timeout)
    print(json.dumps(report, sort_keys=True))
    # 0 means the candidate is advertised, never permission to acquire a frame.
    return {"candidate_advertised": 0, "unsupported": 2, "unavailable": 3}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
