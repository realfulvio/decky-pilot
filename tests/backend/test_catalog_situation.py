import base64
import io
import json

import pytest
from PIL import Image

from backend.catalog import discover
from backend.errors import RpcError
from backend.providers import Registry
from backend.service import Service
from backend.situation import interpret
from backend.storage import DEFAULTS
from conftest import FakeTransport


def scene(**patch):
    return {
        "observations": ["A blue door is visible."],
        "inferences": ["The door may be the route forward."],
        "goal": "Find a route",
        "obstacle": "A closed door",
        "steps": ["Try the lever beside the door."],
        "clarification": "",
        "phase": "gameplay",
        "useful": True,
        **patch,
    }


@pytest.mark.parametrize(
    "provider,data,ids,vision",
    [
        (
            "chatgpt",
            {
                "models": [
                    {
                        "slug": "gpt-6.1-sol",
                        "display_name": "Account model name",
                        "visibility": "list",
                    },
                    {"slug": "hidden", "display_name": "Hidden", "visibility": "hide"},
                    {"slug": "unverified", "display_name": "Another name", "visibility": "list"},
                ]
            },
            ["gpt-6.1-sol", "unverified"],
            [True, False],
        ),
        (
            "grok",
            {
                "models": [
                    {"id": "service-vision", "input_modalities": ["text", "image"]},
                    {"id": "service-text", "input_modalities": ["text"]},
                ]
            },
            ["service-vision", "service-text"],
            [True, False],
        ),
        ("openai", {"data": [{"id": "account-custom"}]}, ["account-custom"], [False]),
        (
            "claude",
            {"data": [{"id": "claude-sonnet-4-6", "display_name": "Name from API"}]},
            ["claude-sonnet-4-6"],
            [True],
        ),
        (
            "gemini",
            {
                "models": [
                    {
                        "name": "models/gemini-3.1-flash-lite",
                        "displayName": "Server name",
                        "supportedGenerationMethods": ["generateContent"],
                    },
                    {"name": "models/embed-only", "supportedGenerationMethods": ["embedContent"]},
                ]
            },
            ["gemini-3.1-flash-lite"],
            [True],
        ),
        ("ollama", {"models": [{"name": "installed-model"}]}, ["installed-model"], [False]),
    ],
)
async def test_native_catalogs_preserve_service_identifiers_and_image_gates(
    provider, data, ids, vision
):
    transport = FakeTransport(data)
    adapter = Registry(transport).get(provider)
    settings = {**DEFAULTS, "provider": provider, "remoteConsent": True, "endpointConsent": True}
    result = await discover(adapter, settings, {provider: "synthetic"})
    assert [m["id"] for m in result["models"]] == ids
    assert [m["images"] for m in result["models"]] == vision
    assert transport.calls[0]["method"] == "GET" and transport.calls[0]["body"] is None
    if provider == "chatgpt":
        assert result["models"][0]["label"] == "Account model name"
    if provider == "grok":
        assert transport.calls[0]["url"] == "https://api.x.ai/v1/language-models"


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"models": "bad"},
        {"models": [{"id": "bad id", "input_modalities": ["image"]}]},
        {"models": [{"id": "same"}, {"id": "same"}]},
    ],
)
async def test_catalog_errors_never_invent_models(data):
    adapter = Registry(FakeTransport(data)).get("grok")
    with pytest.raises(RpcError):
        await discover(adapter, {**DEFAULTS, "remoteConsent": True}, {"grok": "synthetic"})
    assert adapter.catalog is None


async def test_claude_catalog_follows_bounded_cursor_without_changing_host():
    class Pages(FakeTransport):
        async def request(self, url, headers, body=None, **kwargs):
            self.data = {"data": [{"id": "first", "display_name": "First"}], "has_more": True, "last_id": "first"} if "?" not in url else {
                "data": [{"id": "second", "display_name": "Second"}], "has_more": False}
            return await super().request(url, headers, body, **kwargs)
    transport = Pages()
    adapter = Registry(transport).get("claude")
    result = await discover(adapter, {**DEFAULTS, "remoteConsent": True}, {"claude": "synthetic"})
    assert [model["label"] for model in result["models"]] == ["First", "Second"]
    assert transport.calls[-1]["url"] == "https://api.anthropic.com/v1/models?after_id=first"
    assert not result["partial"]


async def test_grok_real_rest_image_shape_and_unsupported_gate():
    transport = FakeTransport(
        {
            "status": "completed",
            "output": [{"type": "message", "content": [{"type": "output_text", "text": "Advice"}]}],
        }
    )
    adapter = Registry(transport).get("grok")
    adapter.catalog = [{"id": "from-account", "images": True}]
    settings = {**DEFAULTS, "model": "from-account", "remoteConsent": True, "visionConfirmed": True}
    image = {"bytes": b"authorized synthetic bytes", "mime": "image/jpeg"}
    await adapter.generate(
        settings, {"grok": "synthetic"}, "policy", [{"role": "user", "content": "help"}], image
    )
    call = transport.calls[0]
    assert call["url"] == "https://api.x.ai/v1/responses" and call["body"]["store"] is False
    assert call["headers"]["Authorization"] == "Bearer synthetic"
    assert call["body"]["input"][-1]["content"][1]["type"] == "input_image"
    adapter.catalog = [{"id": "from-account", "images": False}]
    with pytest.raises(RpcError) as error:
        await adapter.generate(
            settings, {"grok": "synthetic"}, "policy", [{"role": "user", "content": "help"}], image
        )
    assert error.value.code == "IMAGE_UNSUPPORTED" and len(transport.calls) == 1


def test_ambiguous_scene_one_question_and_observation_deduction_separation():
    result = interpret(
        json.dumps(scene(clarification="Which objective is active?", phase="unknown")),
        has_image=True,
    )
    assert result["situation"]["steps"] == [] and result["answer"].count("?") == 1
    assert "Visible:" in result["answer"] and "Possible explanation:" in result["answer"]
    with pytest.raises(RpcError):
        interpret(json.dumps(scene(clarification="Which quest? Which door?")), has_image=True)
    with pytest.raises(RpcError):
        interpret(json.dumps(scene()), has_image=False)


async def setup_service(tmp_path, clock, transport):
    service = Service(tmp_path, clock=clock, transport=transport)
    await service.rpc("set_api_key", {"provider": "openai", "key": "synthetic"})
    await service.rpc("update_settings", {"provider": "openai", "model": "gpt-4.1"})
    await service.rpc(
        "update_settings", {"remoteConsent": True, "visionConfirmed": True, "imagesEnabled": True}
    )
    await service.rpc(
        "set_game_context", {"title": "Synthetic puzzle", "objective": "Find a route"}
    )
    return service


async def image_request(service, clock, request_id="situation"):
    image = Image.new("RGB", (20, 20), "navy")
    output = io.BytesIO()
    image.save(output, format="PNG")
    destination = service.destination()
    prepared = await service.rpc(
        "prepare_image",
        {
            "sessionId": service.context["sessionId"],
            "dataBase64": base64.b64encode(output.getvalue()).decode(),
            "mime": "image/png",
        },
    )
    ref = prepared["data"]["imageRef"]
    await service.rpc(
        "approve_image_send",
        {"sessionId": service.context["sessionId"], "imageRef": ref, "destination": destination},
    )
    return {
        "requestId": request_id,
        "sessionId": service.context["sessionId"],
        "contextRevision": service.context["revision"],
        "text": "Help me now",
        "imageRef": ref,
    }


async def test_obsolete_frame_and_revocation_prevent_network(tmp_path, clock):
    transport = FakeTransport()
    service = await setup_service(tmp_path, clock, transport)
    request = await image_request(service, clock)
    clock.now = 46
    assert (await service.rpc("start_assistant_request", request))["error"][
        "code"
    ] == "CONTEXT_STALE"
    request = await image_request(service, clock)
    await service.rpc("update_settings", {"imagesEnabled": False})
    assert (await service.rpc("start_assistant_request", request))["error"][
        "code"
    ] == "CONSENT_REQUIRED"
    assert not transport.calls
    await service.close()


async def test_reported_presence_refreshes_only_matching_steam_context(tmp_path, clock):
    service = await setup_service(tmp_path, clock, FakeTransport())
    await service.rpc("set_game_context", {"title": "Detected game", "appId": "123", "source": "steam_internal"})
    revision = service.context["revision"]
    clock.now = 301
    assert (await service.rpc("observe_active_game", {"appId": "999"}))["error"]["code"] == "CONTEXT_STALE"
    assert (await service.rpc("observe_active_game", {"appId": "123"}))["ok"]
    assert service.context_time == 301 and service.context["revision"] == revision
    await service.rpc("set_game_context", {"title": "Detected game", "appId": "123", "source": "unknown"})
    assert service.paused and not service.auto_session_consent
    assert (await service.rpc("observe_active_game", {"appId": "123"}))["error"]["code"] == "CONTEXT_STALE"
    await service.close()


async def test_clarification_answer_retained_no_repeat_and_game_change(tmp_path, clock):
    data = {
        "status": "completed",
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(
                            scene(clarification="Which objective is active?", phase="unknown")
                        ),
                    }
                ],
            }
        ],
    }
    transport = FakeTransport(data)
    service = await setup_service(tmp_path, clock, transport)
    request = await image_request(service, clock)
    await service.rpc("start_assistant_request", request)
    await service.request_task
    assert service.records["situation"]["result"]["situation"]["clarification"]
    assert service.history[-1]["content"].endswith("Which objective is active?")
    reply = {**request, "requestId": "reply", "text": "I want to open the door"}
    reply["clarificationReply"] = "I want to open the door"
    reply.pop("imageRef")
    transport.data["output"][0]["content"][0]["text"] = json.dumps(
        scene(observations=[], clarification="", steps=["Try the nearby lever."])
    )
    await service.rpc("start_assistant_request", reply)
    await service.request_task
    assert service.history[-2]["content"] == "I want to open the door"
    assert "Which objective is active?" in str(transport.calls[-1]["body"]["input"])
    assert service.clarification_answers[-1]["playerAnswer"] == "I want to open the door"
    service.history[:] = [{"role": "user", "content": "Later conversation"}] * 20
    await service.rpc("start_assistant_request", {**reply, "requestId": "later", "text": "Next step?", "clarificationReply": ""})
    assert service.active is None
    later = {**reply, "requestId": "later", "text": "Next step?"}
    later.pop("clarificationReply")
    await service.rpc("start_assistant_request", later)
    await service.request_task
    assert "I want to open the door" in str(transport.calls[-1]["body"]["input"])
    transport.data["output"][0]["content"][0]["text"] = json.dumps(
        scene(observations=[], clarification="What have you tried?", phase="unknown")
    )
    await service.rpc("start_assistant_request", {**later, "requestId": "another-question"})
    await service.request_task
    transport.data["output"][0]["content"][0]["text"] = json.dumps(
        scene(observations=[], clarification="Which objective is active?", phase="unknown")
    )
    await service.rpc("start_assistant_request", {**later, "requestId": "repeated-question", "clarificationReply": "The lever"})
    await service.request_task
    assert service.records["repeated-question"]["error"]["code"] == "CONTEXT_NEEDED"
    await service.rpc("set_game_context", {"title": "Other game"})
    assert (
        not service.history and not service.last_clarification and not service.auto_session_consent
    )
    assert (await service.rpc("start_assistant_request", request))["error"][
        "code"
    ] == "CONTEXT_STALE"
    assert not service.clarification_answers and not service.pending_clarification
    await service.rpc("delete_local_data", {"confirm": True})
    assert not service.clarification_answers
    await service.close()


@pytest.mark.parametrize(
    "phase,useful", [("menu", True), ("loading", True), ("unknown", True), ("gameplay", False)]
)
async def test_automatic_abstains_for_menus_loading_and_no_new_advice(
    tmp_path, clock, phase, useful
):
    transport = FakeTransport(
        {
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(scene(observations=[], phase=phase, useful=useful)),
                        }
                    ],
                }
            ],
        }
    )
    service = await setup_service(tmp_path, clock, transport)
    await service.rpc(
        "set_auto_hints",
        {"enabled": True, "consent": True, "sessionId": service.context["sessionId"]},
    )
    clock.now = 90
    service.last_tick = 90
    assert await service.tick()
    await service.request_task
    assert not service.history and service.next_auto == 180
    if phase in ("menu", "loading"):
        assert service.paused
    clock.now = 179
    service.last_tick = 179
    assert await service.tick() is None
    await service.close()
