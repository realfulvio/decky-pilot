import json
import os
import stat
import tempfile
from pathlib import Path

from .errors import RpcError, require, string

PROVIDERS = ("openai", "gemini", "claude", "ollama")
DEFAULTS = {
    "uiLanguage": "en", "responseLanguage": "en", "ttsLanguage": "en", "captureEnabled": False,
    "schemaVersion": 1, "provider": None, "model": "", "remoteConsent": False,
    "ollamaEndpoint": "http://127.0.0.1:11434", "endpointConsent": False,
    "visionConfirmed": False, "spoiler": "full_solutions", "popupDurationMs": 6000,
    "hintIntervalSeconds": 90, "voiceEnabled": True, "ttsEngine": "local",
    "ttsConsent": False, "ttsModel": "gpt-4o-mini-tts", "ttsVoice": "coral",
    "volume": 0.8, "persistentHistory": False, "imagesEnabled": False,
    "autoHints": False, "ollamaTimeoutSeconds": 90,
}


def validate_settings(patch):
    require(isinstance(patch, dict) and set(patch) <= set(DEFAULTS) - {"schemaVersion"})
    for key, value in patch.items():
        if isinstance(DEFAULTS[key], bool):
            require(type(value) is bool)
        elif key in {"uiLanguage", "responseLanguage", "ttsLanguage"}:
            require(value in ("en", "it"))
        elif key in {"model", "ttsModel", "ttsVoice"}:
            string(value, 150)
            require(all(c.isalnum() or c in "._:/-" for c in value))
        elif key == "provider":
            require(value in (*PROVIDERS, None))
        elif key == "spoiler":
            require(value in ("none", "hints", "full_solutions"))
        elif key == "ttsEngine":
            require(value in ("local", "openai"))
        elif key == "ollamaEndpoint":
            from .transport import validate_endpoint
            validate_endpoint(value)
        elif key in {"popupDurationMs", "hintIntervalSeconds", "ollamaTimeoutSeconds"}:
            limits = {"popupDurationMs": (2000, 15000), "hintIntervalSeconds": (90, 3600),
                      "ollamaTimeoutSeconds": (45, 120)}[key]
            require(type(value) is int and limits[0] <= value <= limits[1])
        elif key == "volume":
            require(type(value) in (float, int) and 0 <= value <= 1)
    return patch


class PrivateStore:
    """Plaintext fallback with atomic writes. No claim of encryption or local isolation."""
    def __init__(self, root):
        self.root = Path(root)
        self._check(self.root, directory=True)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._check(self.root, directory=True)
        if os.name == "posix":
            self.root.chmod(0o700)

    def _check(self, path, directory=False):
        require(not any(p.is_symlink() for p in (path, *path.parents)), "STORAGE_ERROR")
        if path.exists():
            info = path.stat()
            require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode),
                    "STORAGE_ERROR")
            if os.name == "posix":
                require(info.st_uid == os.getuid(), "STORAGE_ERROR")

    def read(self, name, default):
        path = self.root / name
        self._check(path)
        if not path.exists():
            return default
        try:
            require(path.stat().st_size <= 2_000_000, "STORAGE_ERROR")
            if os.name == "posix":
                require(path.stat().st_mode & 0o077 == 0, "STORAGE_ERROR")
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise RpcError("STORAGE_ERROR") from exc

    def write(self, name, value):
        path = self.root / name
        self._check(self.root, directory=True)
        self._check(path)
        descriptor, temporary = tempfile.mkstemp(dir=self.root, prefix=".atomic-")
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as file:
                json.dump(value, file, ensure_ascii=False)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, path)
            if os.name == "posix":
                path.chmod(0o600)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def delete(self, name):
        path = self.root / name
        self._check(path)
        path.unlink(missing_ok=True)


class Configuration:
    def __init__(self, store):
        self.store = store
        saved = store.read("settings.json", {})
        require(isinstance(saved, dict), "STORAGE_ERROR")
        version = saved.pop("schemaVersion", 0)
        require(version in (0, 1), "STORAGE_ERROR")
        try:
            validate_settings(saved)
        except RpcError as exc:
            raise RpcError("STORAGE_ERROR") from exc
        self.settings = {**DEFAULTS, **saved}
        self.secrets = store.read("secrets.json", {})
        require(isinstance(self.secrets, dict) and set(self.secrets) <= set(PROVIDERS),
                "STORAGE_ERROR")
        require(all(isinstance(v, str) and 1 <= len(v) <= 4096 for v in self.secrets.values()),
                "STORAGE_ERROR")

    def public(self):
        return {**self.settings, "configured": {p: bool(self.secrets.get(p)) for p in PROVIDERS}}

    def update(self, patch):
        settings = {**self.settings, **validate_settings(patch)}
        # Recipient/model changes always require renewed consent and capability confirmation.
        if any(settings[k] != self.settings[k] for k in ("provider", "model", "ollamaEndpoint")):
            settings.update(remoteConsent=False, endpointConsent=False, visionConfirmed=False,
                            autoHints=False)
        if any(settings[k] != self.settings[k] for k in ("ttsEngine", "ttsModel", "ttsVoice")):
            settings["ttsConsent"] = False
        self.store.write("settings.json", settings)
        self.settings = settings
        return self.public()

    def set_key(self, provider, key):
        require(provider in PROVIDERS and provider != "ollama")
        string(key, 4096, 1)
        require("\n" not in key and "\r" not in key)
        secrets = {**self.secrets, provider: key}
        self.store.write("secrets.json", secrets)
        self.secrets = secrets
        return {"configured": True}

    def delete_key(self, provider):
        require(provider in PROVIDERS)
        secrets = {k: v for k, v in self.secrets.items() if k != provider}
        if secrets:
            self.store.write("secrets.json", secrets)
        else:
            self.store.delete("secrets.json")
        self.secrets = secrets
        return {"configured": False}
