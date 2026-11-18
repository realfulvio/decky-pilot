import asyncio

from test_service import configured, finish, request


class FakeVoice:
    def __init__(self):
        self.gate = asyncio.Event()
        self.stops = 0
        self.called = False

    def capabilities(self):
        return {"local": True, "openai": True, "syntheticVoice": True}

    async def synthesize(self, text, settings, secrets):
        self.called = True
        await self.gate.wait()
        return {"audioBase64": "UklGRjAwMDBXQVZF", "mime": "audio/wav"}

    async def stop(self):
        self.stops += 1


async def test_tts_ready_stop_and_session_change_cleanup(tmp_path, clock, transport):
    service, events = await configured(tmp_path, clock, transport)
    voice = FakeVoice()
    service.tts = voice
    await service.rpc("start_assistant_request", request(service))
    await finish(service)
    args = {"requestId": "request-1", "sessionId": service.context["sessionId"]}
    assert (await service.rpc("start_tts", args))["ok"]
    voice.gate.set()
    await service.tts_task
    assert service.tts_state["state"] == "ready" and service.tts_state["audioBase64"]
    assert any(name == "tts_state" and data.get("state") == "ready" for name, data in events)
    await service.rpc("stop_tts", {})
    assert service.tts_state == {"state": "idle"}
    voice.gate.clear()
    await service.rpc("start_tts", args)
    await asyncio.sleep(0)
    assert voice.called
    await service.rpc("set_game_context", {"title": "Another title"})
    assert service.tts_state["state"] == "idle" and service.tts_task is None
    assert not (await service.rpc("start_tts", args))["ok"]
    await service.close()


async def test_pending_tts_revoked_by_settings(tmp_path, clock, transport):
    service, _ = await configured(tmp_path, clock, transport)
    service.tts = FakeVoice()
    await service.rpc("start_assistant_request", request(service))
    await finish(service)
    await service.rpc("start_tts", {"requestId": "request-1", "sessionId": service.context["sessionId"]})
    await asyncio.sleep(0)
    await service.rpc("update_settings", {"ttsConsent": False, "voiceEnabled": False})
    assert service.tts_task is None and service.tts_state["state"] == "idle"
    assert service.tts.stops >= 2
    await service.close()
