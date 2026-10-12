"""Four native REST adapters. No live calls during offline tests or startup."""
import base64
from urllib.parse import quote

from .errors import RpcError, require
from .storage import PROVIDERS
from .transport import check_response, validate_endpoint


def normalize(answer, usage=None, input_key="input_tokens", output_key="output_tokens"):
    require(isinstance(answer, str) and bool(answer.strip()), "PROVIDER_BLOCKED")
    require(len(answer) <= 16000, "NETWORK_ERROR")
    tokens = {}
    if isinstance(usage, dict):
        for source, target in ((input_key, "inputTokens"), (output_key, "outputTokens")):
            if type(usage.get(source)) is int and usage[source] >= 0:
                tokens[target] = usage[source]
    return {"answer": answer.strip(), "usage": tokens}


def image_data(image):
    return base64.b64encode(image["bytes"]).decode("ascii")


class Provider:
    id = ""

    def __init__(self, transport):
        self.transport = transport

    def validate_config(self, settings, secrets):
        require(settings["model"], "NOT_CONFIGURED")
        if self.id == "ollama":
            require(settings["endpointConsent"], "CONSENT_REQUIRED")
            validate_endpoint(settings["ollamaEndpoint"])
        else:
            require(settings["remoteConsent"], "CONSENT_REQUIRED")
            require(bool(secrets.get(self.id)), "NOT_CONFIGURED")

    def capabilities(self, settings):
        return {"text": True, "images": settings["visionConfirmed"], "structured": False,
                "model": settings["model"], "verification": "user_confirmed" if
                settings["visionConfirmed"] else "unconfirmed"}

    async def post(self, url, headers, body, settings, *, method="POST"):
        response = await self.transport.request(url, headers, body,
            private=self.id == "ollama",
            deadline=settings["ollamaTimeoutSeconds"] if self.id == "ollama" else 45,
            method=method)
        return check_response(response).json()


class OpenAI(Provider):
    id = "openai"

    async def generate(self, settings, secrets, system, messages, image=None, auto=False):
        self.validate_config(settings, secrets)
        items = [{"role": m["role"], "content": m["content"]} for m in messages]
        if image:
            items[-1]["content"] = [
                {"type": "input_text", "text": messages[-1]["content"]},
                {"type": "input_image", "image_url":
                 f"data:{image['mime']};base64,{image_data(image)}"}]
        data = await self.post("https://api.openai.com/v1/responses",
            {"Authorization": f"Bearer {secrets[self.id]}"},
            {"model": settings["model"], "instructions": system, "input": items,
             "store": False, "max_output_tokens": 200 if auto else 1200}, settings)
        try:
            require(data.get("status", "completed") == "completed", "PROVIDER_BLOCKED")
            text = "\n".join(block["text"] for item in data.get("output", [])
                             if item.get("type") == "message"
                             for block in item.get("content", [])
                             if block.get("type") == "output_text")
            return normalize(text, data.get("usage"))
        except (KeyError, TypeError, AttributeError) as exc:
            raise RpcError("NETWORK_ERROR") from exc


class Gemini(Provider):
    id = "gemini"

    async def generate(self, settings, secrets, system, messages, image=None, auto=False):
        self.validate_config(settings, secrets)
        contents = [{"role": "model" if m["role"] == "assistant" else "user",
                     "parts": [{"text": m["content"]}]} for m in messages]
        if image:
            contents[-1]["parts"].append({"inlineData": {"mimeType": image["mime"],
                                                         "data": image_data(image)}})
        model = quote(settings["model"].removeprefix("models/"), safe="")
        data = await self.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            {"x-goog-api-key": secrets[self.id]},
            {"systemInstruction": {"parts": [{"text": system}]}, "contents": contents,
             "generationConfig": {"maxOutputTokens": 200 if auto else 1200}}, settings)
        try:
            require(not data.get("promptFeedback", {}).get("blockReason"), "PROVIDER_BLOCKED")
            candidates = data.get("candidates", [])
            require(bool(candidates), "PROVIDER_BLOCKED")
            candidate = candidates[0]
            require(candidate.get("finishReason", "STOP") in ("STOP", "MAX_TOKENS"),
                    "PROVIDER_BLOCKED")
            text = "\n".join(p["text"] for p in candidate.get("content", {}).get("parts", [])
                             if "text" in p and not p.get("thought"))
            return normalize(text, data.get("usageMetadata"), "promptTokenCount",
                             "candidatesTokenCount")
        except (KeyError, TypeError, AttributeError) as exc:
            raise RpcError("NETWORK_ERROR") from exc


class Claude(Provider):
    id = "claude"

    async def generate(self, settings, secrets, system, messages, image=None, auto=False):
        self.validate_config(settings, secrets)
        items = [{"role": m["role"], "content": m["content"]} for m in messages]
        if image:
            items[-1]["content"] = [
                {"type": "image", "source": {"type": "base64", "media_type": image["mime"],
                                             "data": image_data(image)}},
                {"type": "text", "text": messages[-1]["content"]}]
        data = await self.post("https://api.anthropic.com/v1/messages",
            {"x-api-key": secrets[self.id], "anthropic-version": "2023-06-01"},
            {"model": settings["model"], "system": system, "messages": items,
             "max_tokens": 200 if auto else 1200}, settings)
        try:
            require(data.get("stop_reason") not in ("refusal", "tool_use"), "PROVIDER_BLOCKED")
            text = "\n".join(p["text"] for p in data.get("content", []) if p.get("type") == "text")
            return normalize(text, data.get("usage"))
        except (KeyError, TypeError, AttributeError) as exc:
            raise RpcError("NETWORK_ERROR") from exc


class Ollama(Provider):
    id = "ollama"

    async def inspect_model(self, settings, secrets):
        self.validate_config(settings, secrets)
        data = await self.post(settings["ollamaEndpoint"].rstrip("/") + "/api/show", {},
                               {"model": settings["model"]}, settings)
        capabilities = data.get("capabilities", [])
        require(isinstance(capabilities, list), "NETWORK_ERROR")
        return {"text": "completion" in capabilities, "images": "vision" in capabilities,
                "structured": False, "model": settings["model"], "verification": "api/show"}

    async def generate(self, settings, secrets, system, messages, image=None, auto=False):
        self.validate_config(settings, secrets)
        items = [{"role": "system", "content": system},
                 *[{"role": m["role"], "content": m["content"]} for m in messages]]
        if image:
            capability = await self.inspect_model(settings, secrets)
            require(capability["images"], "IMAGE_UNSUPPORTED")
            items[-1]["images"] = [image_data(image)]
        data = await self.post(settings["ollamaEndpoint"].rstrip("/") + "/api/chat", {},
            {"model": settings["model"], "messages": items, "stream": False,
             "options": {"num_predict": 200 if auto else 1200}}, settings)
        try:
            require(not data.get("error"), "MODEL_UNAVAILABLE")
            return normalize(data.get("message", {}).get("content", ""), data,
                             "prompt_eval_count", "eval_count")
        except (TypeError, AttributeError) as exc:
            raise RpcError("NETWORK_ERROR") from exc


class Registry:
    def __init__(self, transport):
        self.adapters = {cls.id: cls(transport) for cls in (OpenAI, Gemini, Claude, Ollama)}

    def get(self, provider):
        require(provider in PROVIDERS, "NOT_CONFIGURED")
        return self.adapters[provider]
