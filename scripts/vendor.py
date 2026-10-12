"""Fetch one hash-pinned Linux CPython 3.11 wheel. Run at build time, never on the Deck."""
import hashlib
import json
import urllib.request
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
WHEEL = "pillow-12.3.0-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl"
URL = "https://files.pythonhosted.org/packages/3b/2d/ede717bc1144f63886c21fd349bb95860b0d1a21149ff16f2bb362b612b6/" + WHEEL
SHA256 = "23d27a3e0307ec2244cc51e7287b919aa68d097504ebe19df4e76a98a3eea5bd"


def vendor():
    cache = ROOT / ".api-cache" / WHEEL
    cache.parent.mkdir(exist_ok=True)
    if not cache.exists():
        with urllib.request.urlopen(URL, timeout=45) as response:
            data = response.read(20_000_001)
        if len(data) > 20_000_000 or hashlib.sha256(data).hexdigest() != SHA256:
            raise ValueError("Wheel checksum/size mismatch")
        cache.write_bytes(data)
    if hashlib.sha256(cache.read_bytes()).hexdigest() != SHA256:
        raise ValueError("Cached wheel checksum mismatch")
    output = ROOT / "vendor" / "py_modules"
    output.mkdir(parents=True, exist_ok=True)
    with ZipFile(cache) as archive:
        for info in archive.infolist():
            target = output / info.filename
            if not target.resolve().is_relative_to(output.resolve()):
                raise ValueError("Unsafe wheel path")
        archive.extractall(output)
    (output / "deckpilot-vendor.json").write_text(json.dumps({"wheel": WHEEL, "sha256": SHA256,
        "target": "Linux x86_64 glibc>=2.28 CPython3.11"}, indent=2), encoding="utf-8")
    print(f"Verified and vendored {WHEEL}")


if __name__ == "__main__":
    vendor()
