"""Audit shipped Python pins against public OSV advisories; fail if unavailable."""
import json
import urllib.request

PINS = {"PyJWT": "2.15.1", "cryptography": "50.0.2", "cffi": "2.0.0",
        "pycparser": "2.23", "Pillow": "12.3.0"}


def audit():
    failures = []
    for name, version in PINS.items():
        request = urllib.request.Request("https://api.osv.dev/v1/query", headers={"Content-Type": "application/json"},
            data=json.dumps({"package": {"ecosystem": "PyPI", "name": name}, "version": version}).encode())
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read(2_000_001))
        if not isinstance(data, dict) or not isinstance(data.get("vulns", []), list):
            raise ValueError("Runtime dependency audit unavailable")
        failures.extend(f"{name}: {entry['id']}" for entry in data.get("vulns", []))
    if failures:
        raise ValueError("Runtime advisories: " + ", ".join(failures))
    print("Python runtime audit: no advisories for five shipped pins")


if __name__ == "__main__":
    audit()
