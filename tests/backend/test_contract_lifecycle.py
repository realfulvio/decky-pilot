import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import jsonschema

from backend.errors import RpcError
from test_service import configured, finish, request

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "contracts/rpc-v1.schema.json").read_text())
FIXTURE = json.loads((ROOT / "tests/fixtures/contract.json").read_text())


def validate(kind, value):
    jsonschema.validate(value, {**SCHEMA, "$ref": f"#/definitions/{kind}"})


def test_shared_contract_and_safe_error():
    for kind, value in FIXTURE.items():
        validate(kind, value)
    validate("error", RpcError("RATE_LIMITED", 12000).payload())


async def test_actual_rpc_and_events_match_contract(tmp_path, clock, transport):
    service, events = await configured(tmp_path, clock, transport)
    validate("context", service.context)
    payload = request(service, kind="manual")
    validate("request", payload)
    await service.rpc("start_assistant_request", payload)
    await finish(service)
    result = service.records[payload["requestId"]]["result"]
    validate("result", result)
    assert [data for name, data in events if name == "assistant_result"] == [result]
    await service.close()


async def test_decky_loader_import_and_lifecycle(tmp_path, monkeypatch):
    events = []

    async def emit(*args):
        events.append(args)
    monkeypatch.setitem(sys.modules, "decky", SimpleNamespace(
        DECKY_PLUGIN_SETTINGS_DIR=str(tmp_path), DECKY_PLUGIN_RUNTIME_DIR=str(tmp_path / "runtime"), emit=emit))
    # Same file loading pattern as sandboxed_plugin.py, with an unrelated cwd.
    monkeypatch.chdir(tmp_path)
    spec = importlib.util.spec_from_file_location("deckpilot_entry", ROOT / "main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    plugin = module.Plugin()
    await plugin._migration()
    await plugin._main()
    original = plugin.service
    await plugin._main()
    assert plugin.service is original
    status = await plugin.rpc("get_status", {})
    assert status["ok"] and not status["data"]["settings"]["provider"]
    await plugin._unload()
    assert original.closed and original.scheduler is None and plugin.service is None
    await plugin._uninstall()
