"""Conservative tracked-source scan. Never prints matching content."""
import argparse
import io
import re
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [re.compile(rb"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
            re.compile(rb"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{32,}"),
            re.compile(rb"\bAIza[A-Za-z0-9_-]{30,}"),
            re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})"),
            re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
            re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{24,}"),
            # Exact SSRF rejection fixture, never a production credential.
            re.compile(rb"\b(?:https?|ssh)://(?!user:pass@localhost\b)[^\s/:]+:[^\s/@]+@")]


def scan():
    names = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT).split(b"\0")
    failed = []
    for name in names:
        if not name:
            continue
        path = ROOT / name.decode("utf-8")
        if path.is_file() and any(pattern.search(path.read_bytes()) for pattern in PATTERNS):
            failed.append(path.relative_to(ROOT).as_posix())
    if failed:
        raise SystemExit("Possible secret in files (values suppressed): " + ", ".join(failed))
    print("Source secret scan passed; no credentials printed")


def scan_history():
    """Scan every reachable blob and commit, without exposing matching values."""
    objects = subprocess.check_output(["git", "rev-list", "--objects", "--all"], cwd=ROOT)
    identifiers = [line.split(b" ", 1)[0] for line in objects.splitlines()]
    data = subprocess.check_output(["git", "cat-file", "--batch"],
                                   input=b"\n".join(identifiers) + b"\n", cwd=ROOT)
    stream = io.BytesIO(data)
    counts = {"blob": 0, "commit": 0, "images": 0}
    failed = []
    for _ in identifiers:
        identifier, kind, size = stream.readline().split()
        payload = stream.read(int(size))
        assert stream.read(1) == b"\n"
        if kind not in (b"blob", b"commit"):
            continue
        counts[kind.decode()] += 1
        if any(pattern.search(payload) for pattern in PATTERNS):
            failed.append(identifier.decode() + ": credential pattern")
        if payload.startswith(b"\x89PNG\r\n\x1a\n") or payload.startswith(b"\xff\xd8\xff"):
            counts["images"] += 1
            with Image.open(io.BytesIO(payload)) as image:
                image.load()
                if image.getexif() or any(key.lower() in {"exif", "gps", "comment", "description"}
                                         for key in image.info):
                    failed.append(identifier.decode() + ": image metadata requires review")
    # The public history must not include accidentally tracked runtime/cache files.
    paths = [line.split(b" ", 1)[1] for line in objects.splitlines() if b" " in line]
    private_names = {b".env", b"secrets.json", b"settings.json", b"history.json",
                     b"id_rsa", b"id_ed25519", b"node_modules", b".venv", b".api-cache"}
    if any(private_names.intersection(path.replace(b"\\", b"/").split(b"/")) for path in paths):
        failed.append("tracked runtime/cache/private filename")
    if failed:
        raise SystemExit("Publication review required (values suppressed): " + ", ".join(failed))
    print(f"Reachable history scan passed: {counts['commit']} commits, "
          f"{counts['blob']} blobs, {counts['images']} decoded images; values suppressed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", action="store_true")
    args = parser.parse_args()
    scan()
    if args.history:
        scan_history()
