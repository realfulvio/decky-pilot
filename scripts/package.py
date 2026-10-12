"""Allowlist-only, deterministic installable Decky archive (one top-level directory)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]


def package():
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    output = ROOT / "artifacts" / f"deckpilot-{manifest['version']}.zip"
    output.parent.mkdir(exist_ok=True)
    files = [(ROOT / name, name) for name in ("main.py", "plugin.json", "package.json", "README.md", "LICENSE")]
    for folder in ("backend", "dist", "docs", "contracts", "third_party"):
        for file in sorted((ROOT / folder).rglob("*")):
            if file.is_file() and "__pycache__" not in file.parts and file.suffix != ".pyc":
                files.append((file, file.relative_to(ROOT).as_posix()))
    for file in sorted((ROOT / "vendor" / "py_modules").rglob("*")):
        if file.is_file() and "__pycache__" not in file.parts and file.suffix != ".pyc":
            files.append((file, "py_modules/" + file.relative_to(ROOT / "vendor/py_modules").as_posix()))
    if not (ROOT / "dist/index.js").is_file() or not (ROOT / "vendor/py_modules/PIL").is_dir():
        raise ValueError("Run frontend build and scripts/vendor.py first")
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for file, name in sorted(files, key=lambda item: item[1]):
            if file.is_symlink():
                raise ValueError("Symlink in package inputs")
            info = ZipInfo("DeckPilot/" + name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, file.read_bytes())
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".zip.sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    source = output.with_name(f"deckpilot-{manifest['version']}-source.zip")
    subprocess.run(["git", "archive", "--format=zip", "HEAD", "-o", str(source)],
                   cwd=ROOT, check=True)
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    source.with_suffix(".zip.sha256").write_text(f"{source_digest}  {source.name}\n", encoding="utf-8")
    print(f"{output.name}: {output.stat().st_size} bytes; SHA256 {digest}")
    return output


if __name__ == "__main__":
    output = package()
    sys.path.insert(0, str(ROOT / "scripts"))
    from verify_package import verify
    verify(output)
