"""Explicit, credential-scoped model discovery. Names/IDs always come from the service."""
from urllib.parse import urlencode
from .errors import require, string
from .providers import VISION_MODELS


async def discover(provider, settings, secrets):
    # Catalog retrieval requires endpoint/network consent, but no selected model.
    provider.validate_config({**settings, "model": settings["model"] or "catalog"}, secrets)
    name = provider.id
    if name == "ollama":
        data = await provider.post(settings["ollamaEndpoint"].rstrip("/") + "/api/tags", {}, None, settings, method="GET")
        rows = data.get("models")
    elif name == "gemini":
        data = await provider.post("https://generativelanguage.googleapis.com/v1beta/models",
                                  {"x-goog-api-key": secrets[name]}, None, settings, method="GET")
        rows = data.get("models")
    elif name == "claude":
        data = await provider.post("https://api.anthropic.com/v1/models",
            {"x-api-key": secrets[name], "anthropic-version": "2023-06-01"}, None, settings, method="GET")
        rows = data.get("data")
    else:
        url = "https://api.x.ai/v1/language-models" if name == "grok" else "https://api.openai.com/v1/models"
        data = await provider.post(url, {"Authorization": f"Bearer {secrets[name]}"}, None, settings, method="GET")
        rows = data.get("models" if name in ("chatgpt", "grok") else "data")
    require(isinstance(rows, list) and len(rows) <= 2000, "NETWORK_ERROR")
    seen_cursors = set()
    # Follow only the documented catalog cursors; never a service-supplied URL.
    for _ in range(19):
        cursor = data.get("last_id") if name == "claude" and data.get("has_more") else data.get("nextPageToken") if name == "gemini" else None
        if not cursor:
            break
        cursor = string(cursor, 2000, 1)
        require(cursor not in seen_cursors, "NETWORK_ERROR")
        seen_cursors.add(cursor)
        if name == "claude":
            url = "https://api.anthropic.com/v1/models?" + urlencode({"after_id": cursor})
            headers = {"x-api-key": secrets[name], "anthropic-version": "2023-06-01"}
            row_key = "data"
        else:
            url = "https://generativelanguage.googleapis.com/v1beta/models?" + urlencode({"pageToken": cursor})
            headers = {"x-goog-api-key": secrets[name]}
            row_key = "models"
        data = await provider.post(url, headers, None, settings, method="GET")
        page = data.get(row_key)
        require(isinstance(page, list) and len(rows) + len(page) <= 2000, "NETWORK_ERROR")
        rows = rows + page
    models = []
    for row in rows:
        require(isinstance(row, dict), "NETWORK_ERROR")
        if name == "chatgpt" and row.get("visibility") != "list":
            continue
        if name == "gemini" and "generateContent" not in row.get("supportedGenerationMethods", []):
            continue
        identifier = string(row.get("slug") if name == "chatgpt" else row.get("name") if name in ("gemini", "ollama") else row.get("id"), 150, 1)
        if name == "gemini":
            identifier = identifier.removeprefix("models/")
        require(all(c.isalnum() or c in "._:/-" for c in identifier), "NETWORK_ERROR")
        label = string(row.get("display_name") if name == "chatgpt" else row.get("displayName", identifier) if name == "gemini" else row.get("display_name", identifier), 200, 1)
        documented = any(m["id"] == identifier for m in VISION_MODELS.get(name, []))
        modalities = row.get("input_modalities")
        images = "image" in modalities if name == "grok" and isinstance(modalities, list) else documented
        models.append({"id": identifier, "label": label, "images": bool(images),
                       "verification": "catalog_modalities" if name == "grok" else "official_docs" if documented else "unconfirmed"})
    require(len({m["id"] for m in models}) == len(models), "NETWORK_ERROR")
    # Label a bounded traversal that is still partial. Never invent/select entries.
    provider.catalog = models
    return {"models": models, "partial": bool(data.get("has_more") or data.get("nextPageToken"))}
