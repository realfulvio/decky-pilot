"""Optional Gamescope CLI capture. No framebuffer, keys, X11 writes or installs.

Source: ValveSoftware/gamescope 1b17fcc1b6ba4b657d39cf374d287191e40476b0.
The screenshot command defaults to BASE_PLANE_ONLY. Target hardware is untested.
"""
import asyncio
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path

from .errors import RpcError, require
from .storage import PrivateStore

# The upstream command is not atomically bound to a specific app/window.
# Focus checks before/after cannot prove that an account screen was never captured
# during a transition. Keep acquisition unavailable until this safety gate is met.
# See docs/CAPTURE_VERIFICATION.md. Test doubles never enable production capture.
CAPTURE_SAFETY_VALIDATED = False


class GameCapture:
    def __init__(self, root, spawn=asyncio.create_subprocess_exec):
        self.root = Path(root)
        self.spawn = spawn
        self.cli = shutil.which("gamescopectl")
        self.xprop = shutil.which("xprop")
        self.available = False
        self.probed = False
        self.process = None

    async def command(self, *args, output=False):
        process = await self.spawn(*args, stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE if output else asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL)
        self.process = process
        try:
            async with asyncio.timeout(3):
                data = await process.stdout.read(131073) if output else b""
                require(len(data) <= 131072, "CAPTURE_UNAVAILABLE")
                require(await process.wait() == 0, "CAPTURE_UNAVAILABLE")
                return data.decode("utf-8", errors="replace")
        finally:
            if process.returncode is None:
                process.kill()
                await process.wait()
            self.process = None

    async def probe(self):
        # Runtime discovery/cache is not evidence of atomic game-surface binding.
        if not CAPTURE_SAFETY_VALIDATED:
            self.available = False
            return False
        if self.probed:
            return self.available
        self.probed = True
        if not sys.platform.startswith("linux") or not self.cli or not self.xprop:
            return False
        # Do not connect to a remote X server or another user's compositor.
        if not re.fullmatch(r":\d+(?:\.\d+)?", os.environ.get("DISPLAY", "")):
            return False
        runtime = Path(f"/run/user/{os.getuid()}")
        display = os.environ.get("GAMESCOPE_WAYLAND_DISPLAY", "gamescope-0")
        if not re.fullmatch(r"gamescope-\d+", display) or os.environ.get("XDG_RUNTIME_DIR") != str(runtime):
            return False
        try:
            socket_path = runtime / display
            require(not any(p.is_symlink() for p in (socket_path, *socket_path.parents)), "CAPTURE_UNAVAILABLE")
            info = socket_path.stat()
            require(stat.S_ISSOCK(info.st_mode) and info.st_uid == os.getuid(), "CAPTURE_UNAVAILABLE")
            help_text = await self.command(self.cli, "help", output=True)
            self.available = CAPTURE_SAFETY_VALIDATED and bool(re.search(r"\bscreenshot\b", help_text))
        except (OSError, RpcError, TimeoutError):
            self.available = False
        return self.available

    async def assert_game(self, context):
        require(self.available, "CAPTURE_UNAVAILABLE")
        app_id = context.get("appId", "")
        require(context.get("source") == "steam_internal" and app_id.isascii() and
                app_id.isdigit() and int(app_id) not in (0, 769), "CAPTURE_BLOCKED")
        data = await self.command(self.xprop, "-root", "GAMESCOPE_FOCUSED_APP",
                                  "GAMESCOPE_FOCUSED_APP_GFX", output=True)
        values = re.findall(r"GAMESCOPE_FOCUSED_APP(?:_GFX)?\(CARDINAL\)\s*=\s*(\d+)\s*(?:\n|$)", data)
        require(len(values) == 2 and all(int(value) == int(app_id) for value in values), "CAPTURE_BLOCKED")

    async def capture(self, context):
        # Enforce the release gate at acquisition, even if a probe is stale/wrong.
        require(CAPTURE_SAFETY_VALIDATED, "CAPTURE_UNAVAILABLE")
        await self.probe()
        await self.assert_game(context)
        store = PrivateStore(self.root)
        # A unique private destination avoids the shared /tmp/gamescope.png path.
        with tempfile.TemporaryDirectory(prefix="frame-", dir=store.root) as temporary:
            target = Path(temporary) / "game.png"
            require(target.resolve().is_relative_to(store.root.resolve()), "STORAGE_ERROR")
            try:
                await self.command(self.cli, "screenshot", str(target))
                async with asyncio.timeout(5):
                    # CLI completion precedes the async writer; bounded filesystem polling.
                    from .images import Image
                    complete = False
                    for _ in range(100):
                        if target.exists():
                            store._check(target)
                            require(target.stat().st_size <= 5 * 1024 * 1024, "INVALID_INPUT")
                            try:
                                with Image.open(target) as image:
                                    require(image.width * image.height <= 20_000_000, "INVALID_INPUT")
                                    image.verify()
                                complete = True
                                break
                            except OSError:
                                pass
                        await asyncio.sleep(0.05)
                    require(complete, "CAPTURE_UNAVAILABLE")
                await self.assert_game(context)
                descriptor = os.open(target, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                with os.fdopen(descriptor, "rb") as file:
                    data = file.read(5 * 1024 * 1024 + 1)
                require(len(data) <= 5 * 1024 * 1024, "INVALID_INPUT")
                return data
            except (OSError, TimeoutError) as exc:
                raise RpcError("CAPTURE_UNAVAILABLE") from exc
