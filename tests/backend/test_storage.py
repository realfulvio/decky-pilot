import json
import os

import pytest

from backend.errors import RpcError
from backend.storage import Configuration, DEFAULTS, PrivateStore


def test_defaults_migration_secrets_atomic_delete(tmp_path):
    store = PrivateStore(tmp_path / "private")
    config = Configuration(store)
    assert config.settings == DEFAULTS
    assert DEFAULTS["popupDurationMs"] == 6000 and DEFAULTS["hintIntervalSeconds"] == 90
    assert DEFAULTS["spoiler"] == "full_solutions" and DEFAULTS["voiceEnabled"]
    assert not DEFAULTS["imagesEnabled"] and not DEFAULTS["persistentHistory"]
    config.set_key("openai", "synthetic-key")
    assert "synthetic-key" not in json.dumps(config.public())
    assert config.public()["configured"]["openai"] is True
    assert not list(store.root.glob(".atomic-*"))
    if os.name == "posix":
        assert store.root.stat().st_mode & 0o777 == 0o700
        assert (store.root / "secrets.json").stat().st_mode & 0o777 == 0o600
    config.delete_key("openai")
    assert not (store.root / "secrets.json").exists()
    store.write("settings.json", {"schemaVersion": 0, "spoiler": "hints"})
    migrated = Configuration(store)
    assert migrated.settings["schemaVersion"] == 1 and migrated.settings["spoiler"] == "hints"


@pytest.mark.parametrize("patch", [{"hintIntervalSeconds": 89}, {"hintIntervalSeconds": True},
    {"hintIntervalSeconds": 90.0}, {"provider": "fake"}, {"model": "bad\nmodel"}, {"volume": float("nan")},
    {"remoteConsent": "true"}, {"imagesEnabled": 1}, {"schemaVersion": 9}, {"unknown": "key"},
    {"popupDurationMs": 0}, {"ollamaTimeoutSeconds": 1000}])
def test_invalid_settings(tmp_path, patch):
    config = Configuration(PrivateStore(tmp_path))
    with pytest.raises(RpcError):
        config.update(patch)
    assert config.settings == DEFAULTS


def test_recipient_revokes_consent(tmp_path):
    config = Configuration(PrivateStore(tmp_path))
    config.update({"provider": "openai", "model": "configured-model"})
    config.update({"remoteConsent": True, "visionConfirmed": True, "autoHints": True})
    config.update({"provider": "gemini"})
    assert not config.settings["remoteConsent"] and not config.settings["visionConfirmed"]
    assert not config.settings["autoHints"]


def test_corrupt_and_future_files_not_reset(tmp_path):
    store = PrivateStore(tmp_path)
    path = tmp_path / "settings.json"
    path.write_text("broken", encoding="utf-8")
    if os.name == "posix":
        path.chmod(0o600)
    with pytest.raises(RpcError):
        Configuration(store)
    assert path.read_text() == "broken"
    store.write("settings.json", {"schemaVersion": 999})
    with pytest.raises(RpcError):
        Configuration(store)


def test_symlink_rejected(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "unsafe"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("Windows workstation has no symlink privilege; Linux CI covers this")
    with pytest.raises(RpcError):
        PrivateStore(link)
    store = PrivateStore(target)
    outside = tmp_path / "outside.json"
    outside.write_text('{}')
    (target / "secrets.json").symlink_to(outside)
    with pytest.raises(RpcError):
        Configuration(store)
    with pytest.raises(RpcError):
        store.write("secrets.json", {"key": "never"})
