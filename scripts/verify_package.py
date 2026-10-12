import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

REQUIRED = {"DeckPilot/main.py", "DeckPilot/plugin.json", "DeckPilot/package.json", "DeckPilot/dist/index.js",
            "DeckPilot/backend/service.py", "DeckPilot/backend/providers.py", "DeckPilot/LICENSE",
            "DeckPilot/py_modules/PIL/_imaging.cpython-311-x86_64-linux-gnu.so",
            "DeckPilot/py_modules/deckpilot-vendor.json"}
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
        if "SP_REACT" not in bundle or "HARNESS OFFLINE" in bundle or "FakeBridge" in bundle:
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


if __name__ == "__main__":
    verify(sys.argv[1])
