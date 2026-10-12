"""Thin Decky lifecycle/RPC adapter. Domain modules import without the Loader."""
import sys
from pathlib import Path

# Decky loads this file with spec_from_file_location, not as a normal package.
PLUGIN_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PLUGIN_ROOT))
sys.path.insert(0, str(PLUGIN_ROOT / "py_modules"))

from backend.service import Service  # noqa: E402


class Plugin:
    def __init__(self):
        self.service = None

    async def _main(self):
        import decky
        if self.service is None:
            runtime = Path(decky.DECKY_PLUGIN_RUNTIME_DIR) / "import-images"
            self.service = Service(decky.DECKY_PLUGIN_SETTINGS_DIR, emit=decky.emit, import_root=runtime)
            await self.service.start()

    async def rpc(self, method, payload):
        if self.service is None:
            await self._main()
        return await self.service.rpc(method, payload)

    async def _unload(self):
        if self.service:
            await self.service.close()
            self.service = None

    async def _uninstall(self):
        # Retain settings unless explicitly deleted by the user before uninstall.
        await self._unload()

    async def _migration(self):
        # Schema migration is owned by Configuration and never silently resets corrupt data.
        pass
