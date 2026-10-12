import json

from .errors import fields, require, string

from .i18n import LANGUAGES, translate
from .situation import SCHEMA_INSTRUCTION


def validate_context(value):
    fields(value, ("title", "appId", "objective", "location", "userNotes", "source", "newSession"))
    title = string(value.get("title"), 200, 1)
    require(bool(title))
    app_id = string(value.get("appId", ""), 20)
    require(not app_id or app_id.isascii() and app_id.isdigit())
    source = value.get("source", "manual")
    require(source in ("manual", "steam_internal", "unknown"))
    require(type(value.get("newSession", False)) is bool)
    notes = {key: string(value.get(key, ""), 4000) for key in
             ("objective", "location", "userNotes")}
    require(sum(map(len, notes.values())) <= 8000)
    return {"title": title, "appId": app_id, "source": source, **notes}


def build_context(context, history, text, spoiler, auto=False, language="en"):
    require(language in LANGUAGES)
    system = translate("policy", language).format(language="English" if language == "en" else "italiano",
        spoiler=spoiler, spoilerPolicy=translate("spoilerPolicy." + spoiler, language))
    if auto:
        system += translate("autoPolicy", language)
    system += SCHEMA_INSTRUCTION
    data = {key: context[key] for key in ("title", "appId", "objective", "location", "userNotes")}
    # Budget deterministic: max 12 history messages, at most 8000 history characters.
    budget, recent = 8000, []
    for entry in reversed(history[-12:]):
        content = entry["content"][:min(4000, budget)]
        if not content:
            break
        recent.append({"role": entry["role"], "content": content})
        budget -= len(content)
    messages = list(reversed(recent))
    messages.append({"role": "user", "content": translate("contextPrefix", language) + "\n" +
                     json.dumps(data, ensure_ascii=False) + "\n" + translate("questionPrefix", language) + "\n" + text})
    return system, messages
