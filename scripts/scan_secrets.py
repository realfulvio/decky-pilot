"""Conservative tracked-source scan. Never prints matching content."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [re.compile(rb"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
            re.compile(rb"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{32,}"),
            re.compile(rb"\bAIza[A-Za-z0-9_-]{30,}")]


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


if __name__ == "__main__":
    scan()
