import asyncio
import copy
import hashlib
import base64
import os
import stat
import json
import time
import uuid
from datetime import datetime, timezone

from .capture import GameCapture
from .context import build_context, validate_context
from .errors import RpcError, fields, require, string
from .images import Images
from .providers import Registry
from .storage import Configuration, DEFAULTS, PrivateStore
from .transport import Transport
from .tts import TTS
from .i18n import translate


def popup_text(answer, language="en"):
    normalized = " ".join(answer.split())
    if len(normalized) <= 180:
        return normalized
    return normalized[:170].rsplit(" ", 1)[0] + "… " + translate("openPanel", language)


class Service:
    def __init__(self, root, emit=None, transport=None, clock=time.monotonic,
                 wall_clock=time.time, tts=None, import_root=None, capture=None):
        self.store = PrivateStore(root)
        self.config = Configuration(self.store)
        self.transport = transport or Transport()
        self.registry = Registry(self.transport)
        self.clock, self.wall_clock = clock, wall_clock
        self.emit_callback = emit
        self.images = Images(clock)
        self.import_store = PrivateStore(import_root or self.store.root / "import-images")
        self.tts = tts or TTS(self.transport)
        self.capture = capture or GameCapture(self.import_store.root.parent / "capture-images")
        self.capture_task = None
        self.capture_blocked = True
        self.auto_session_consent = False
        self.auto_visual = False
        self.lock = asyncio.Lock()
        self.context = None
        self.context_time = 0
        self.history = []
        self.records = {}
        self.active = None
        self.request_task = None
        self.tts_task = None
        self.tts_state = {"state": "idle"}
        self.scheduler = None
        self.closed = False
        self.paused = False
        self.auto_attempts = 0
        self.auto_errors = 0
        self.last_hint_revision = -1
        self.auto_seen = set()
        self.next_auto = clock() + self.config.settings["hintIntervalSeconds"]
        self.retry_until = 0
        self.last_tick = clock()
        self.archive = self.store.read("history.json", {})
        require(isinstance(self.archive, dict), "STORAGE_ERROR")
        self.prune_history()

    async def emit(self, event, payload):
        if self.emit_callback and not self.closed:
            try:
                await self.emit_callback(event, payload)
            except Exception:
                # State is retained for polling recovery; never log content or raw exceptions.
                pass

    def destination(self):
        settings = self.config.settings
        return {"provider": settings["provider"], "model": settings["model"],
                "endpoint": settings["ollamaEndpoint"] if settings["provider"] == "ollama" else "cloud"}

    def prune_history(self):
        cutoff = self.wall_clock() - 7 * 86400
        if self.config.settings["persistentHistory"]:
            self.history = [m for m in self.history if m["at"] >= cutoff][-100:]
        changed = False
        for key in list(self.archive):
            value = self.archive[key]
            require(isinstance(value, list), "STORAGE_ERROR")
            require(all(isinstance(m, dict) and set(m) == {"role", "content", "at"} and
                        m["role"] in ("user", "assistant") and isinstance(m["content"], str) and
                        len(m["content"]) <= 16000 and type(m["at"]) in (float, int)
                        for m in value), "STORAGE_ERROR")
            retained = [m for m in value if m["at"] >= cutoff][-100:]
            changed |= retained != value
            if retained:
                self.archive[key] = retained
            else:
                self.archive.pop(key)
                changed = True
        if changed and self.archive:
            self.store.write("history.json", self.archive)
        elif changed:
            self.store.delete("history.json")

    def persist_history(self):
        if self.config.settings["persistentHistory"] and self.context:
            self.archive[self.context["gameKey"]] = self.history[-100:]
            # Bound archive globally as well as per-game.
            while len(self.archive) > 20:
                self.archive.pop(next(iter(self.archive)))
            while len(json.dumps(self.archive, ensure_ascii=False).encode("utf-8")) > 1_800_000:
                self.archive.pop(next(iter(self.archive)))
            self.store.write("history.json", self.archive)

    async def get_status(self, payload):
        fields(payload, ())
        return {"schemaVersion": 1, "settings": self.config.public(), "context": self.context,
                "history": self.history[-100:], "requests": list(self.records.values())[-100:],
                "pendingImageRef": next(iter(self.images.items), None),
                "active": self.active, "tts": self.tts_state,
                "auto": {"paused": self.paused, "attempts": self.auto_attempts,
                         "limit": 20, "errors": self.auto_errors,
                         "sessionConsent": self.auto_session_consent, "visual": self.auto_visual},
                "capabilities": {"capture": await self.capture.probe(), "images": self.images.available,
                                 "importRoot": str(self.import_store.root),
                                 "tts": self.tts.capabilities()},
                "diagnostics": {"storage": "plaintext_private_files", "hardwareValidated": False,
                                "effectiveUid": getattr(os, "geteuid", lambda: -1)(),
                                "historyContextLimit": 12, "historyCharacterLimit": 8000,
                                "inputCharacterLimit": 4000, "notesCharacterLimit": 8000}}

    async def get_settings(self, payload):
        fields(payload, ())
        return self.config.public()

    async def update_settings(self, payload):
        # Serialize revocation with generation admission. Any settings edit invalidates images.
        async with self.lock:
            result = self.config.update(payload)
            self.auto_session_consent = False
            await self.cancel_active()
            await self.stop_voice()
            self.images.clear()
            self.next_auto = self.clock() + result["hintIntervalSeconds"]
            if not result["persistentHistory"]:
                self.archive.clear()
                self.store.delete("history.json")
            else:
                self.persist_history()
            return result

    async def set_api_key(self, payload):
        fields(payload, ("provider", "key"))
        async with self.lock:
            result = self.config.set_key(payload.get("provider"), payload.get("key"))
            self.auto_session_consent = False
            await self.cancel_active()
            await self.stop_voice()
            self.images.clear()
            return result

    async def delete_api_key(self, payload):
        fields(payload, ("provider",))
        async with self.lock:
            result = self.config.delete_key(payload.get("provider"))
            self.auto_session_consent = False
            await self.cancel_active()
            await self.stop_voice()
            self.images.clear()
            return result

    async def set_game_context(self, payload):
        data = validate_context(payload)
        async with self.lock:
            key = hashlib.sha256((data["appId"] or data["title"].casefold()).encode()).hexdigest()[:24]
            previous = self.context
            new = not previous or previous["gameKey"] != key or payload.get("newSession", False)
            meaningful = new or any(data[k] != previous[k] for k in data)
            if not meaningful:
                return previous
            await self.cancel_active()
            await self.stop_voice()
            self.images.clear()
            if new:
                self.persist_history()
                self.prune_history()
                self.history = copy.deepcopy(self.archive.get(key, [])) if self.config.settings[
                    "persistentHistory"] else []
                self.auto_attempts = self.auto_errors = 0
                self.last_hint_revision = -1
                self.auto_seen.clear()
                self.paused = False
                self.auto_session_consent = False
                self.auto_visual = False
                self.next_auto = self.clock() + self.config.settings["hintIntervalSeconds"]
                self.records.clear()
            self.context_time = self.clock()
            self.context = {**data, "gameKey": key,
                            "sessionId": str(uuid.uuid4()) if new else previous["sessionId"],
                            "revision": 1 if new else previous["revision"] + 1,
                            "observedAt": datetime.fromtimestamp(self.wall_clock(), timezone.utc).isoformat()}
            await self.emit("context_changed", self.context)
            return self.context

    async def start_assistant_request(self, payload):
        async with self.lock:
            # Automatic admission is backend-only; the public RPC cannot bypass scheduling.
            require(payload.get("kind", "manual") == "manual")
            return await self.start_request(payload)

    async def start_request(self, payload, auto=False):
        fields(payload, ("requestId", "sessionId", "contextRevision", "kind", "text", "imageRef"))
        request_id = string(payload.get("requestId"), 100, 1)
        require(bool(request_id) and all(c.isalnum() or c in "_-" for c in request_id))
        require(self.context is not None, "CONTEXT_STALE")
        require(payload.get("sessionId") == self.context["sessionId"] and
                type(payload.get("contextRevision")) is int and
                payload["contextRevision"] == self.context["revision"], "CONTEXT_STALE")
        if request_id in self.records:
            return self.records[request_id]
        require(not self.active, "BUSY")
        require(self.clock() >= self.retry_until, "RATE_LIMITED")
        text = string(payload.get("text"), 4000, 1)
        require(bool(text))
        settings, secrets = copy.deepcopy(self.config.settings), dict(self.config.secrets)
        provider = self.registry.get(settings["provider"])
        provider.validate_config(settings, secrets)
        image = None
        if payload.get("imageRef"):
            ref = string(payload["imageRef"], 100, 1)
            require(settings["imagesEnabled"], "CONSENT_REQUIRED")
            require(provider.capabilities(settings)["images"], "IMAGE_UNSUPPORTED")
            image = self.images.take(ref, self.context["sessionId"], self.destination())
        context = dict(self.context)
        system, messages = build_context(context, self.history, text, settings["spoiler"], auto, settings["responseLanguage"])
        record = {"requestId": request_id, "sessionId": context["sessionId"],
                  "contextRevision": context["revision"], "kind": "auto_hint" if auto else "manual",
                  "state": "pending"}
        self.records[request_id] = record
        while len(self.records) > 100:
            self.records.pop(next(iter(self.records)))
        self.active = request_id
        self.request_task = asyncio.create_task(self.generate(record, context, settings, secrets,
                                                               provider, system, messages, image, text))
        await self.emit("request_state", record)
        return dict(record)

    async def generate(self, record, context, settings, secrets, provider, system, messages, image, text):
        request_id = record["requestId"]
        try:
            if record["kind"] == "auto_hint" and self.auto_visual:
                require(self.auto_session_consent and not self.capture_blocked, "CONSENT_REQUIRED")
                raw = await self.capture.capture(context)
                require(self.auto_session_consent and not self.capture_blocked and self.context and
                        self.context["sessionId"] == context["sessionId"] and
                        self.context["revision"] == context["revision"], "CONTEXT_STALE")
                digest = hashlib.sha256(raw).hexdigest()
                if digest in self.auto_seen:
                    record["state"] = "duplicate"
                    return
                self.auto_seen.add(digest)
                prepared = self.images.prepare(base64.b64encode(raw).decode("ascii"), "image/png",
                    context["sessionId"], self.destination())
                self.images.approve(prepared["imageRef"], context["sessionId"], self.destination())
                image = self.images.take(prepared["imageRef"], context["sessionId"], self.destination())
            async with asyncio.timeout(settings["ollamaTimeoutSeconds"] if provider.id == "ollama" else 45):
                output = await provider.generate(settings, secrets, system, messages, image,
                                                 record["kind"] == "auto_hint")
            if not self.context or (self.context["sessionId"], self.context["revision"]) != (
                    context["sessionId"], context["revision"]):
                raise RpcError("CONTEXT_STALE")
            answer = output["answer"]
            normalized = " ".join(answer.casefold().split())
            if record["kind"] == "auto_hint" and normalized in self.auto_seen:
                record["state"] = "duplicate"
                return
            if record["kind"] == "auto_hint":
                self.auto_seen.add(normalized)
                self.auto_errors = 0
            result = {"schemaVersion": 1, "requestId": request_id,
                      "sessionId": context["sessionId"], "contextRevision": context["revision"],
                      "provider": provider.id, "model": settings["model"], **output,
                      "popupText": popup_text(answer, settings["responseLanguage"]), "speechText": answer[:1000]}
            record.update(state="completed", result=result)
            self.history.extend([
                {"role": "user", "content": text, "at": self.wall_clock()},
                {"role": "assistant", "content": answer, "at": self.wall_clock()}])
            self.history = self.history[-100:]
            self.persist_history()
            await self.emit("assistant_result", result)
        except asyncio.CancelledError:
            record.update(state="cancelled", error=RpcError("CANCELLED").payload(self.config.settings["uiLanguage"]))
        except Exception as exc:
            error = exc if isinstance(exc, RpcError) else RpcError(
                "TIMEOUT" if isinstance(exc, TimeoutError) else "INTERNAL_ERROR")
            record.update(state="error", error=error.payload(self.config.settings["uiLanguage"]))
            if error.code == "RATE_LIMITED":
                self.retry_until = self.clock() + (error.retry_after_ms or 90000) / 1000
            if record["kind"] == "auto_hint":
                self.auto_errors += 1
                if self.auto_errors >= 3:
                    self.paused = True
            await self.emit("assistant_error", {"requestId": request_id,
                "sessionId": record["sessionId"], "contextRevision": record["contextRevision"],
                "error": error.payload(self.config.settings["uiLanguage"])})
        finally:
            if self.active == request_id:
                self.active = None
            # Images and key snapshots exist only for the admitted task's lifetime.
            await self.emit("request_state", record)

    async def cancel_active(self):
        if self.capture_task and not self.capture_task.done():
            self.capture_task.cancel()
            await asyncio.gather(self.capture_task, return_exceptions=True)
        self.capture_task = None
        if self.request_task and not self.request_task.done():
            self.request_task.cancel()
            await asyncio.gather(self.request_task, return_exceptions=True)
        self.active = None
        self.request_task = None

    async def cancel_request(self, payload):
        fields(payload, ("requestId", "sessionId"))
        async with self.lock:
            record = self.records.get(payload.get("requestId"))
            require(record and self.context and record["sessionId"] == payload.get("sessionId") ==
                    self.context["sessionId"], "CONTEXT_STALE")
            if self.active == record["requestId"]:
                await self.cancel_active()
            return dict(record)

    async def set_auto_hints(self, payload):
        fields(payload, ("enabled", "paused", "resetBudget", "sessionId", "consent", "visual"))
        require(all(type(v) is bool for k, v in payload.items() if k != "sessionId"))
        async with self.lock:
            if "enabled" in payload:
                if payload["enabled"]:
                    require(self.context and payload.get("sessionId") == self.context["sessionId"] and
                            payload.get("consent") is True, "CONSENT_REQUIRED")
                    if payload.get("visual"):
                        require(self.config.settings["captureEnabled"] and
                                self.config.settings["imagesEnabled"], "CONSENT_REQUIRED")
                        require(await self.capture.probe(), "CAPTURE_UNAVAILABLE")
                        require(self.registry.get(self.config.settings["provider"]).capabilities(
                            self.config.settings)["images"], "IMAGE_UNSUPPORTED")
                    self.registry.get(self.config.settings["provider"]).validate_config(
                        self.config.settings, self.config.secrets)
                    self.auto_visual = payload.get("visual", False)
                    self.auto_session_consent = True
                else:
                    self.auto_session_consent = False
                self.config.update({"autoHints": payload["enabled"]})
            if "paused" in payload:
                self.paused = payload["paused"]
            if payload.get("resetBudget"):
                self.auto_attempts = self.auto_errors = 0
            self.next_auto = self.clock() + self.config.settings["hintIntervalSeconds"]
            if (self.paused or not self.config.settings["autoHints"]) and self.active and self.records[
                    self.active]["kind"] == "auto_hint":
                await self.cancel_active()
            return {"enabled": self.config.settings["autoHints"], "paused": self.paused,
                    "attempts": self.auto_attempts}

    async def tick(self):
        async with self.lock:
            self.images.prune()
            self.prune_history()
            now = self.clock()
            if now - self.last_tick > 15:
                self.next_auto = now + self.config.settings["hintIntervalSeconds"]
            self.last_tick = now
            ctx = self.context
            if (self.closed or not self.config.settings["autoHints"] or self.paused or not ctx or
                not self.auto_session_consent or (self.auto_visual and self.capture_blocked) or
                self.active or ctx["source"] == "unknown" or
                self.tts_state["state"] not in ("idle", "error") or
                now < max(self.next_auto, self.retry_until) or self.auto_attempts >= 20 or
                self.last_hint_revision == ctx["revision"] or now - self.context_time > 300 or
                not any(ctx[k] for k in ("objective", "location", "userNotes"))):
                return None
            # Reserve before creating a task. Failures consume the cooldown and budget too.
            self.next_auto = now + self.config.settings["hintIntervalSeconds"]
            self.last_hint_revision = ctx["revision"]
            self.auto_attempts += 1
            try:
                return await self.start_request({"requestId": uuid.uuid4().hex,
                    "sessionId": ctx["sessionId"], "contextRevision": ctx["revision"],
                    "text": translate("visualPrompt" if self.auto_visual else "hintPrompt",
                                      self.config.settings["responseLanguage"])}, auto=True)
            except RpcError:
                self.auto_errors += 1
                if self.auto_errors >= 3:
                    self.paused = True
                return None

    async def run_scheduler(self):
        try:
            while not self.closed:
                await asyncio.sleep(5)
                await self.tick()
        except asyncio.CancelledError:
            pass

    async def start(self):
        if not self.scheduler:
            self.scheduler = asyncio.create_task(self.run_scheduler())

    async def set_capture_guard(self, payload):
        fields(payload, ("blocked",))
        require(type(payload.get("blocked")) is bool)
        # Set immediately, before awaiting any lock or cancelling capture.
        self.capture_blocked = payload["blocked"]
        if self.capture_blocked:
            if self.capture_task and not self.capture_task.done():
                self.capture_task.cancel()
            if self.auto_visual and self.active:
                await self.cancel_active()
        return {"blocked": self.capture_blocked}

    async def prepare_capture(self, payload):
        fields(payload, ("sessionId", "confirmGameplay"))
        async with self.lock:
            require(payload.get("confirmGameplay") is True and not self.capture_blocked,
                    "CAPTURE_BLOCKED")
            require(self.config.settings["captureEnabled"] and self.config.settings["imagesEnabled"],
                    "CONSENT_REQUIRED")
            require(self.context and payload.get("sessionId") == self.context["sessionId"], "CONTEXT_STALE")
            require(not self.active and not self.capture_task, "BUSY")
            provider = self.registry.get(self.config.settings["provider"])
            provider.validate_config(self.config.settings, self.config.secrets)
            require(provider.capabilities(self.config.settings)["images"], "IMAGE_UNSUPPORTED")
            context, destination = dict(self.context), self.destination()
            task = self.capture_task = asyncio.create_task(self.capture.capture(context))
        try:
            raw = await task
            async with self.lock:
                require(not self.capture_blocked and self.context and
                        (self.context["sessionId"], self.context["revision"]) ==
                        (context["sessionId"], context["revision"]) and
                        destination == self.destination(), "CONTEXT_STALE")
                return await asyncio.to_thread(self.images.prepare, base64.b64encode(raw).decode("ascii"),
                    "image/png", context["sessionId"], destination)
        except asyncio.CancelledError as exc:
            raise RpcError("CANCELLED") from exc
        finally:
            if self.capture_task is task:
                self.capture_task = None

    async def prepare_image(self, payload):
        fields(payload, ("dataBase64", "mime", "sessionId"))
        require(self.context and payload.get("sessionId") == self.context["sessionId"], "CONTEXT_STALE")
        require(self.config.settings["imagesEnabled"], "CONSENT_REQUIRED")
        # Decode off the event loop; serialize with session/settings changes.
        async with self.lock:
            require(self.context and payload.get("sessionId") == self.context["sessionId"],
                    "CONTEXT_STALE")
            require(self.config.settings["imagesEnabled"], "CONSENT_REQUIRED")
            return await asyncio.to_thread(self.images.prepare, payload.get("dataBase64"),
                payload.get("mime"), self.context["sessionId"], self.destination())

    async def approve_image_send(self, payload):
        fields(payload, ("imageRef", "sessionId", "destination"))
        require(self.config.settings["imagesEnabled"], "CONSENT_REQUIRED")
        require(self.context and payload.get("sessionId") == self.context["sessionId"] and
                payload.get("destination") == self.destination(), "CONSENT_REQUIRED")
        return self.images.approve(string(payload.get("imageRef"), 100, 1),
                                   self.context["sessionId"], self.destination())

    def read_import(self, filename):
        name = string(filename, 200, 1)
        require(name == filename and name not in (".", "..") and
                not any(c in name for c in "/\\:") and name.lower().endswith((".png", ".jpg", ".jpeg")))
        path = self.import_store.root / name
        self.import_store._check(path)
        require(path.is_file() and path.resolve().parent == self.import_store.root.resolve())
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(descriptor, "rb") as file:
            require(stat.S_ISREG(os.fstat(file.fileno()).st_mode))
            data = file.read(5 * 1024 * 1024 + 1)
        require(len(data) <= 5 * 1024 * 1024)
        mime = "image/png" if data.startswith(b"\x89PNG\r\n\x1a\n") else "image/jpeg"
        return base64.b64encode(data).decode("ascii"), mime

    async def prepare_import_image(self, payload):
        fields(payload, ("filename", "sessionId"))
        async with self.lock:
            require(self.context and payload.get("sessionId") == self.context["sessionId"],
                    "CONTEXT_STALE")
            require(self.config.settings["imagesEnabled"], "CONSENT_REQUIRED")
            data, mime = await asyncio.to_thread(self.read_import, payload.get("filename"))
            return await asyncio.to_thread(self.images.prepare, data, mime,
                                           self.context["sessionId"], self.destination())

    async def discard_image(self, payload):
        fields(payload, ("imageRef",))
        self.images.discard(string(payload.get("imageRef"), 100, 1))
        return {"discarded": True}

    async def test_provider(self, payload):
        fields(payload, ("confirmCost",))
        require(payload.get("confirmCost") is True, "CONSENT_REQUIRED")
        settings = self.config.settings
        if settings["provider"] == "ollama":
            async with self.lock:
                require(not self.active, "BUSY")
                capability = await self.registry.get("ollama").inspect_model(settings, self.config.secrets)
                self.config.update({"visionConfirmed": capability["images"]})
                return {"capabilities": capability}
        require(self.context is not None, "CONTEXT_STALE")
        return await self.start_assistant_request({"requestId": uuid.uuid4().hex,
            "sessionId": self.context["sessionId"], "contextRevision": self.context["revision"],
            "text": translate("connectionPrompt", settings["responseLanguage"])})

    async def start_tts(self, payload):
        fields(payload, ("requestId", "sessionId"))
        async with self.lock:
            record = self.records.get(payload.get("requestId"))
            require(record and record["state"] == "completed" and self.context and
                    record["sessionId"] == payload.get("sessionId") == self.context["sessionId"] and
                    record["contextRevision"] == self.context["revision"], "CONTEXT_STALE")
            await self.stop_voice()
            settings, secrets = dict(self.config.settings), dict(self.config.secrets)
            state = {"state": "pending", "requestId": record["requestId"],
                     "sessionId": record["sessionId"], "contextRevision": record["contextRevision"]}
            self.tts_state = state
            self.tts_task = asyncio.create_task(self.generate_voice(state, record["result"][
                "speechText"], settings, secrets))
            await self.emit("tts_state", state)
            return dict(state)

    async def generate_voice(self, state, text, settings, secrets):
        try:
            audio = await self.tts.synthesize(text, settings, secrets)
            self.tts_state = {**state, "state": "ready", **audio}
            await self.emit("tts_state", self.tts_state)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            error = exc if isinstance(exc, RpcError) else RpcError("VOICE_UNAVAILABLE")
            self.tts_state = {**state, "state": "error", "error": error.payload(self.config.settings["uiLanguage"])}
            await self.emit("tts_state", self.tts_state)

    async def stop_voice(self):
        if self.tts_task and not self.tts_task.done():
            self.tts_task.cancel()
            await asyncio.gather(self.tts_task, return_exceptions=True)
        await self.tts.stop()
        self.tts_task = None
        self.tts_state = {"state": "idle"}
        await self.emit("tts_state", self.tts_state)

    async def stop_tts(self, payload):
        fields(payload, ())
        async with self.lock:
            await self.stop_voice()
        return self.tts_state

    async def clear_history(self, payload):
        fields(payload, ())
        async with self.lock:
            await self.cancel_active()
            await self.stop_voice()
            self.history.clear()
            self.records.clear()
            self.images.clear()
            if self.context:
                self.archive.pop(self.context["gameKey"], None)
            if self.archive:
                self.store.write("history.json", self.archive)
            else:
                self.store.delete("history.json")
            return {"cleared": True}

    async def delete_local_data(self, payload):
        fields(payload, ("confirm",))
        require(payload.get("confirm") is True)
        async with self.lock:
            await self.cancel_active()
            await self.stop_voice()
            self.images.clear()
            self.context = None
            self.auto_session_consent = False
            self.auto_visual = False
            self.history.clear()
            self.records.clear()
            self.archive.clear()
            self.auto_seen.clear()
            self.auto_attempts = self.auto_errors = 0
            self.retry_until = 0
            for name in ("settings.json", "secrets.json", "history.json"):
                self.store.delete(name)
            self.config.settings = dict(DEFAULTS)
            self.config.secrets.clear()
            await self.emit("context_changed", None)
            return {"deleted": True}

    async def close(self):
        self.closed = True
        if self.scheduler:
            self.scheduler.cancel()
            await asyncio.gather(self.scheduler, return_exceptions=True)
            self.scheduler = None
        await self.cancel_active()
        await self.stop_voice()
        self.images.clear()
        await self.transport.close()

    async def rpc(self, method, payload):
        allowed = {"get_status", "get_settings", "update_settings", "set_api_key", "delete_api_key",
                   "set_game_context", "start_assistant_request", "cancel_request", "set_auto_hints",
                   "prepare_image", "prepare_import_image", "approve_image_send", "discard_image", "test_provider",
                   "prepare_capture", "set_capture_guard", "start_tts", "stop_tts", "clear_history", "delete_local_data"}
        try:
            require(not self.closed, "CANCELLED")
            require(isinstance(method, str) and method in allowed)
            require(isinstance(payload, dict))
            return {"ok": True, "data": await getattr(self, method)(payload)}
        except Exception as exc:
            error = exc if isinstance(exc, RpcError) else RpcError("INTERNAL_ERROR")
            return {"ok": False, "error": error.payload(self.config.settings["uiLanguage"])}
