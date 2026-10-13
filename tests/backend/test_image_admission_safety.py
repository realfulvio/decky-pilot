"""Synthetic image lifecycle and refusal before provider side effects."""
import asyncio
import base64
import threading
from unittest.mock import AsyncMock

import pytest

from backend.images import Images
from test_images_tts_urls import synthetic_image
from test_service import configured, request


@pytest.mark.parametrize("source", ["upload", "import"])
@pytest.mark.parametrize("cleanup", ["revoke", "game", "delete", "close"])
async def test_cancelled_decode_cannot_restore_cleared_images(
        tmp_path, clock, transport, monkeypatch, source, cleanup):
    service, events = await configured(tmp_path, clock, transport)
    await service.rpc("update_settings", {"imagesEnabled": True})
    encoded = synthetic_image(size=(32, 24))
    (service.import_store.root / "selected.png").write_bytes(base64.b64decode(encoded))
    started, finished = asyncio.Event(), asyncio.Event()
    release = threading.Event()
    loop = asyncio.get_running_loop()
    original = Images.prepare

    def delayed(self, *args):
        loop.call_soon_threadsafe(started.set)
        assert release.wait(5), "Test did not release synthetic decoder"
        try:
            return original(self, *args)
        finally:
            loop.call_soon_threadsafe(finished.set)

    monkeypatch.setattr(Images, "prepare", delayed)
    payload = {"sessionId": service.context["sessionId"]}
    if source == "upload":
        method = "prepare_image"
        payload.update(dataBase64=encoded, mime="image/png")
    else:
        method = "prepare_import_image"
        payload["filename"] = "selected.png"
    task = asyncio.create_task(service.rpc(method, payload))
    try:
        await asyncio.wait_for(started.wait(), 2)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        if cleanup == "revoke":
            assert (await service.rpc("update_settings", {"imagesEnabled": False}))["ok"]
        elif cleanup == "game":
            assert (await service.rpc("set_game_context", {"title": "Other game"}))["ok"]
        elif cleanup == "delete":
            assert (await service.rpc("delete_local_data", {"confirm": True}))["ok"]
        else:
            await service.close()
        release.set()
        await asyncio.wait_for(finished.wait(), 2)
        assert not service.images.items
        assert not transport.calls
        assert not any(name == "assistant_result" for name, _ in events)
    finally:
        release.set()
        await asyncio.gather(task, return_exceptions=True)
        await service.close()


@pytest.mark.parametrize("provider", ["ollama", "chatgpt", "grok"])
@pytest.mark.parametrize("state,code", [
    ("unapproved", "CONSENT_REQUIRED"), ("unknown", "CONSENT_REQUIRED"),
    ("destination", "CONSENT_REQUIRED"), ("stale", "CONTEXT_STALE"),
    ("disabled", "CONSENT_REQUIRED"),
])
async def test_image_refusal_precedes_credentials_and_catalog(
        tmp_path, clock, transport, monkeypatch, provider, state, code):
    service, events = await configured(tmp_path, clock, transport)
    try:
        await service.rpc("update_settings", {"imagesEnabled": True})
        service.config.settings["provider"] = provider
        prepared = service.images.prepare(synthetic_image(size=(32, 24)), "image/png",
                                           service.context["sessionId"], service.destination())
        ref = prepared["imageRef"]
        if state != "unapproved":
            service.images.approve(ref, service.context["sessionId"], service.destination())
        if state == "unknown":
            ref = "missing-image"
        elif state == "destination":
            service.config.settings["model"] = "changed-model"
        elif state == "stale":
            clock.now = 46
        elif state == "disabled":
            service.config.settings["imagesEnabled"] = False
        credentials = AsyncMock(side_effect=AssertionError("Credentials must not be read"))
        discover = AsyncMock(side_effect=AssertionError("Catalog must not be requested"))
        monkeypatch.setattr(service, "credentials", credentials)
        monkeypatch.setattr("backend.service.discover", discover)
        result = await service.rpc("start_assistant_request", request(service, imageRef=ref))
        assert result["error"]["code"] == code
        credentials.assert_not_awaited()
        discover.assert_not_awaited()
        assert not transport.calls and not service.records and service.active is None
        assert not any(name == "assistant_result" for name, _ in events)
    finally:
        await service.close()


async def test_shutdown_during_decode_refuses_late_success(tmp_path, clock, transport, monkeypatch):
    service, _ = await configured(tmp_path, clock, transport)
    await service.rpc("update_settings", {"imagesEnabled": True})
    started, finished = asyncio.Event(), asyncio.Event()
    release = threading.Event()
    loop = asyncio.get_running_loop()
    original = Images.prepare

    def delayed(self, *args):
        loop.call_soon_threadsafe(started.set)
        assert release.wait(5)
        try:
            return original(self, *args)
        finally:
            loop.call_soon_threadsafe(finished.set)

    monkeypatch.setattr(Images, "prepare", delayed)
    task = asyncio.create_task(service.rpc("prepare_image", {
        "sessionId": service.context["sessionId"], "mime": "image/png",
        "dataBase64": synthetic_image(size=(32, 24))}))
    try:
        await asyncio.wait_for(started.wait(), 2)
        await service.close()
        release.set()
        result = await asyncio.wait_for(task, 2)
        assert result["error"]["code"] == "CANCELLED"
        assert not service.images.items and not transport.calls
    finally:
        release.set()
        await asyncio.gather(task, return_exceptions=True)
        await service.close()


@pytest.mark.parametrize("change,code", [("discard", "CONSENT_REQUIRED"), ("age", "CONTEXT_STALE")])
async def test_image_rechecked_after_credential_await(
        tmp_path, clock, transport, monkeypatch, change, code):
    service, _ = await configured(tmp_path, clock, transport)
    try:
        await service.rpc("update_settings", {"imagesEnabled": True, "visionConfirmed": True})
        prepared = service.images.prepare(synthetic_image(size=(32, 24)), "image/png",
                                           service.context["sessionId"], service.destination())
        ref = prepared["imageRef"]
        service.images.approve(ref, service.context["sessionId"], service.destination())

        async def credentials(settings):
            if change == "discard":
                await service.rpc("discard_image", {"imageRef": ref})
            else:
                clock.now = 46
            return {}

        monkeypatch.setattr(service, "credentials", credentials)
        result = await service.rpc("start_assistant_request", request(service, imageRef=ref))
        assert result["error"]["code"] == code
        assert not transport.calls and not service.records
    finally:
        await service.close()


@pytest.mark.parametrize("invalid", ["truncated", "animated", "oversized"])
async def test_invalid_import_preserves_previous_preview_without_provider(
        tmp_path, clock, transport, monkeypatch, invalid):
    import io

    from PIL import Image

    service, _ = await configured(tmp_path, clock, transport)
    try:
        assert (await service.rpc("update_settings", {
            "provider": None, "imagesEnabled": True}))["ok"]
        credentials = AsyncMock(side_effect=AssertionError("Import needs no credentials"))
        monkeypatch.setattr(service, "credentials", credentials)
        session = service.context["sessionId"]
        root = service.import_store.root
        root.joinpath("good.png").write_bytes(base64.b64decode(synthetic_image(size=(32, 24))))
        prepared = await service.rpc("prepare_import_image", {"sessionId": session, "filename": "good.png"})
        assert prepared["ok"]
        ref = prepared["data"]["imageRef"]
        if invalid == "animated":
            data = io.BytesIO()
            Image.new("RGB", (4, 4), "red").save(data, format="PNG", save_all=True,
                append_images=[Image.new("RGB", (4, 4), "blue")], duration=100)
            raw = data.getvalue()
        elif invalid == "oversized":
            raw = b"\x89PNG\r\n\x1a\n" + b"x" * (5 * 1024 * 1024)
        else:
            raw = base64.b64decode(synthetic_image(size=(32, 24)))[:45]
        root.joinpath("bad.png").write_bytes(raw)
        result = await service.rpc("prepare_import_image", {"sessionId": session, "filename": "bad.png"})
        assert result["error"]["code"] == "INVALID_INPUT"
        assert list(service.images.items) == [ref]
        assert not service.images.items[ref]["approved"]
        assert (await service.rpc("discard_image", {"imageRef": ref}))["ok"]
        assert not service.images.items
        assert root.joinpath("good.png").exists()  # User-owned import source is preserved.
        credentials.assert_not_awaited()
        assert not transport.calls
    finally:
        await service.close()
