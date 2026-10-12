import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

REQUIRED = {"DeckPilot/main.py", "DeckPilot/plugin.json", "DeckPilot/package.json", "DeckPilot/dist/index.js",
            "DeckPilot/backend/service.py", "DeckPilot/backend/providers.py", "DeckPilot/LICENSE",
            "DeckPilot/py_modules/PIL/_imaging.cpython-311-x86_64-linux-gnu.so",
            "DeckPilot/py_modules/deckpilot-vendor.json"}
REQUIRED |= {"DeckPilot/locales/en.json", "DeckPilot/locales/it.json"}
REQUIRED |= {"DeckPilot/docs/licenses/decky-api-LGPL-2.1.txt", "DeckPilot/third_party/decky-api/src/index.ts"}


def verify(path):
    path = Path(path)
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or not REQUIRED <= set(names):
            raise ValueError("Required package files missing or duplicated")
        for name in names:
            parts = PurePosixPath(name).parts
            if not parts or parts[0] != "DeckPilot" or ".." in parts or "\\" in name:
                raise ValueError("Unsafe archive path")
            if any(p in {"node_modules", ".git", ".venv", ".api-cache", "tests", "__pycache__"} for p in parts) or any(
                p.startswith(".env") or p in {"secrets.json", "settings.json", "history.json"} for p in parts):
                raise ValueError("Private/development files in package")
        manifest = json.loads(archive.read("DeckPilot/plugin.json"))
        if manifest.get("flags") != [] or manifest.get("api_version") != 1:
            raise ValueError("Unexpected privileges or API version")
        bundle = archive.read("DeckPilot/dist/index.js").decode()
        if "SP_REACT" not in bundle or "FakeBridge" in bundle:
            raise ValueError("React bundling or harness contamination")
        vendor = json.loads(archive.read("DeckPilot/py_modules/deckpilot-vendor.json"))
        if vendor["sha256"] != "23d27a3e0307ec2244cc51e7287b919aa68d097504ebe19df4e76a98a3eea5bd":
            raise ValueError("Unexpected runtime wheel")
        if archive.testzip() is not None:
            raise ValueError("Corrupt ZIP")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if not path.with_suffix(".zip.sha256").read_text().startswith(digest + "  "):
        raise ValueError("Package checksum mismatch")
    print(f"Verified {len(names)} files: Decky layout, runtime ABI, no development/private files")


def verify_runtime(path):
    """Execute the extracted deliverable, never dependencies from the checkout/venv."""
    if not sys.platform.startswith("linux") or sys.version_info[:2] != (3, 11):
        raise ValueError("Packaged runtime smoke requires Linux CPython 3.11")
    with tempfile.TemporaryDirectory(prefix="deckpilot-package-") as temporary:
        with ZipFile(path) as archive:
            archive.extractall(temporary)
        root = Path(temporary) / "DeckPilot"
        code = '''
import asyncio, importlib.util, io, sys
from pathlib import Path
from types import SimpleNamespace
root = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(root / "py_modules"), str(root)]
from PIL import Image, _imaging
assert Path(Image.__file__).is_relative_to(root / "py_modules")
assert Path(_imaging.__file__).is_relative_to(root / "py_modules")
data = io.BytesIO()
Image.new("RGB", (2, 2), "navy").save(data, format="PNG")
data.seek(0)
with Image.open(data) as decoded:
    decoded.load()
    assert decoded.size == (2, 2)
async def emit(*args):
    pass
sys.modules["decky"] = SimpleNamespace(
    DECKY_PLUGIN_SETTINGS_DIR=str(root / "smoke-settings"),
    DECKY_PLUGIN_RUNTIME_DIR=str(root / "smoke-runtime"), emit=emit)
spec = importlib.util.spec_from_file_location("deckpilot_packaged", root / "main.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
async def smoke():
    plugin = module.Plugin()
    try:
        await plugin._migration()
        await plugin._main()
        status = await plugin.rpc("get_status", {})
        assert status["ok"] and status["data"]["settings"]["provider"] is None
    finally:
        await plugin._unload()
    assert plugin.service is None
asyncio.run(smoke())
print("Extracted ZIP runtime passed: vendored Pillow encode/decode and offline plugin lifecycle")
'''
        subprocess.run([sys.executable, "-I", "-c", code, str(root)],
                       cwd=temporary, check=True, timeout=30)


if __name__ == "__main__":
    verify(sys.argv[1])
    if "--runtime" in sys.argv[2:]:
        verify_runtime(sys.argv[1])
