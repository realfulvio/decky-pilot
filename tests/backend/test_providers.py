import pytest

from backend.errors import RpcError
from backend.providers import Claude, Gemini, Ollama, OpenAI
from backend.storage import DEFAULTS
from conftest import FakeTransport

CASES = [
    (OpenAI, {"output": [{"type": "reasoning", "summary": []}, {"type": "message", "content": [
        {"type": "output_text", "text": "Open"}, {"type": "output_text", "text": "the door."}]}],
        "usage": {"input_tokens": 7, "output_tokens": 3}}, "api.openai.com/v1/responses", "Authorization"),
    (Gemini, {"candidates": [{"content": {"parts": [{"text": "hidden", "thought": True},
        {"text": "Open"}, {"text": "the door."}]}, "finishReason": "STOP"}],
        "usageMetadata": {"promptTokenCount": 7, "candidatesTokenCount": 3}},
        "generativelanguage.googleapis.com/v1beta/models/test-model:generateContent", "x-goog-api-key"),
    (Claude, {"content": [{"type": "thinking", "thinking": "hidden"}, {"type": "text", "text": "Open"},
        {"type": "text", "text": "the door."}], "usage": {"input_tokens": 7, "output_tokens": 3}},
        "api.anthropic.com/v1/messages", "x-api-key"),
    (Ollama, {"message": {"content": "Open\nthe door."}, "prompt_eval_count": 7, "eval_count": 3,
        "capabilities": ["completion", "vision"]}, "127.0.0.1:11434/api/chat", None),
]


@pytest.mark.parametrize("cls,data,url,auth", CASES)
@pytest.mark.parametrize("with_image", [False, True])
async def test_native_protocols(cls, data, url, auth, with_image):
    transport = FakeTransport(data)
    adapter = cls(transport)
    settings = {**DEFAULTS, "provider": cls.id, "model": "test-model", "remoteConsent": True,
                "endpointConsent": True, "visionConfirmed": True}
    image = {"mime": "image/png", "bytes": b"synthetic image"} if with_image else None
    result = await adapter.generate(settings, {cls.id: "synthetic-credential"}, "system policy",
                                    [{"role": "user", "content": "question"}], image)
    assert result == {"answer": "Open\nthe door.", "usage": {"inputTokens": 7, "outputTokens": 3}}
    call = transport.calls[-1]
    assert url in call["url"]
    assert "synthetic-credential" not in call["url"]
    if auth:
        assert "synthetic-credential" in call["headers"][auth]
    body = call["body"]
    if cls is not Gemini:
        assert body["model"] == "test-model"
    if cls is OpenAI:
        assert body["instructions"] == "system policy" and body["store"] is False
        assert body["max_output_tokens"] == 1200
        if image:
            assert body["input"][0]["content"][1]["type"] == "input_image"
    elif cls is Gemini:
        assert body["systemInstruction"]["parts"][0]["text"] == "system policy"
        if image:
            assert body["contents"][0]["parts"][1]["inlineData"]["mimeType"] == "image/png"
    elif cls is Claude:
        assert call["headers"]["anthropic-version"] == "2023-06-01"
        assert body["system"] == "system policy"
        if image:
            assert body["messages"][0]["content"][0]["source"]["type"] == "base64"
    else:
        assert body["stream"] is False and call["private"] is True
        assert body["messages"][0]["role"] == "system"
        if image:
            assert body["messages"][-1]["images"]
            assert transport.calls[0]["url"].endswith("/api/show")


@pytest.mark.parametrize("cls,data,url,auth", CASES)
@pytest.mark.parametrize("status,code", [(401, "AUTH_FAILED"), (403, "AUTH_FAILED"),
    (429, "RATE_LIMITED"), (500, "NETWORK_ERROR"), (404, "MODEL_UNAVAILABLE")])
async def test_errors_sanitized(cls, data, url, auth, status, code):
    transport = FakeTransport({"error": "synthetic-credential PRIVATE_PROMPT"}, status)
    settings = {**DEFAULTS, "model": "test-model", "remoteConsent": True, "endpointConsent": True}
    with pytest.raises(RpcError) as caught:
        await cls(transport).generate(settings, {cls.id: "synthetic-credential"}, "policy",
                                      [{"role": "user", "content": "question"}])
    assert caught.value.code == code
    assert "PRIVATE_PROMPT" not in str(caught.value)
    assert "synthetic-credential" not in str(caught.value)
    if status == 429:
        assert caught.value.retry_after_ms == 12000


@pytest.mark.parametrize("cls,data,url,auth", CASES)
@pytest.mark.parametrize("bad", [b"not-json", b"[]", b'{"output":[null],"candidates":[null],"content":[null],"message":null}', b'{}'])
async def test_malformed_or_empty(cls, data, url, auth, bad):
    settings = {**DEFAULTS, "model": "test-model", "remoteConsent": True, "endpointConsent": True}
    with pytest.raises(RpcError):
        await cls(FakeTransport(bad)).generate(settings, {cls.id: "key"}, "policy",
                                              [{"role": "user", "content": "question"}])


@pytest.mark.parametrize("cls,data,url,auth", CASES)
async def test_consent_config_timeout_and_small_auto_budget(cls, data, url, auth):
    transport = FakeTransport(data)
    settings = {**DEFAULTS, "model": "test-model"}
    with pytest.raises(RpcError) as consent_error:
        await cls(transport).generate(settings, {cls.id: "key"}, "policy", [])
    assert consent_error.value.code == "CONSENT_REQUIRED"
    assert not transport.calls
    settings.update(remoteConsent=True, endpointConsent=True)
    await cls(transport).generate(settings, {cls.id: "key"}, "policy", [{"role": "user", "content": "q"}], auto=True)
    body = transport.calls[-1]["body"]
    assert 200 in (body.get("max_output_tokens"), body.get("max_tokens"),
                   body.get("generationConfig", {}).get("maxOutputTokens"),
                   body.get("options", {}).get("num_predict"))
    with pytest.raises(RpcError) as caught:
        await cls(FakeTransport(error=RpcError("TIMEOUT"))).generate(settings, {cls.id: "key"},
            "policy", [{"role": "user", "content": "q"}])
    assert caught.value.code == "TIMEOUT"


async def test_gemini_block_and_ollama_vision():
    settings = {**DEFAULTS, "model": "test-model", "remoteConsent": True, "endpointConsent": True}
    with pytest.raises(RpcError) as caught:
        await Gemini(FakeTransport({"promptFeedback": {"blockReason": "SAFETY"}})).generate(
            settings, {"gemini": "key"}, "policy", [{"role": "user", "content": "q"}])
    assert caught.value.code == "PROVIDER_BLOCKED"
    transport = FakeTransport({"capabilities": ["completion"]})
    with pytest.raises(RpcError) as caught:
        await Ollama(transport).generate(settings, {}, "policy", [{"role": "user", "content": "q"}],
                                         {"bytes": b"image", "mime": "image/png"})
    assert caught.value.code == "IMAGE_UNSUPPORTED"
    assert len(transport.calls) == 1
