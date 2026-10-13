"""Explicit, bounded headless Gamescope capability experiment; captures no pixels."""

import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import tempfile
import time

from probe_capture_protocols import probe


def main():
    executable = shutil.which("gamescope")
    if not executable:
        print(json.dumps({"status": "gamescope_missing", "capture_safety_validated": False}))
        return 3
    # Prevent core files; all runtime/config state belongs to this disposable instance.
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    artifacts = Path(__file__).resolve().parents[1] / "artifacts"
    artifacts.mkdir(exist_ok=True)
    report = {"status": "startup_timeout", "capture_safety_validated": False}
    with tempfile.TemporaryDirectory(prefix="capture-probe-", dir=artifacts) as temporary:
        root = Path(temporary)
        env = {"PATH": "/usr/bin:/bin", "LANG": "C", "HOME": str(root),
               "XDG_RUNTIME_DIR": str(root), "XDG_CONFIG_HOME": str(root),
               "XDG_DATA_HOME": str(root), "XDG_CACHE_HOME": str(root),
               "gamescope_backend": "'headless'"}
        # No DISPLAY, session bus, PipeWire remote, Wayland parent or inherited secrets.
        # Explicit backend env also overrides Gamescope startup-script backend selection.
        process = subprocess.Popen(
            [executable, "--backend", "headless", "--expose-wayland",
             "-W", "320", "-H", "240"], env=env, cwd=root,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            deadline = time.monotonic() + 10
            path = root / "gamescope-0"
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    report["status"] = "startup_failed"
                    report["exit_code"] = process.returncode
                    break
                if path.is_socket():
                    report = probe(path, timeout=3)
                    break
                time.sleep(0.05)
        finally:
            # This process group contains only this experiment and its Xwayland.
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
            # Also terminate a child left behind if the parent exited first.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=2)
    print(json.dumps(report, sort_keys=True))
    return {"candidate_advertised": 0, "unsupported": 2}.get(report["status"], 3)


if __name__ == "__main__":
    raise SystemExit(main())
