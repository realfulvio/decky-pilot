"""Validate a model's situation estimate; observations remain estimates, not game telemetry."""
import json

from .errors import RpcError, require, string

SCHEMA_INSTRUCTION = """
Return only JSON with keys observations (array of short strings describing visible pixels),
inferences (array of explicitly uncertain deductions), goal (string), obstacle (string),
steps (array of up to 5 concrete short actions), clarification (one brief question or empty string),
phase (gameplay, menu, loading, or unknown), useful (boolean).
When scene/goal is ambiguous, use clarification instead of guessing a solution. Ask just one
relevant question, using the player's previous answers. Do not repeat a question already answered.
If no image is supplied, observations must be empty. Do not infer hidden game state.
For automatic help, set useful=false for menus, loading, ambiguity, or no useful new advice.
"""


def interpret(answer, language="en", has_image=False, require_structured=False):
    value = answer.strip()
    if value.startswith("```json") and value.endswith("```"):
        value = value[7:-3].strip()
    try:
        data = json.loads(value)
    except ValueError as exc:
        if not has_image and not require_structured:
            return {"answer": answer}
        raise RpcError("PROVIDER_BLOCKED") from exc
    require(isinstance(data, dict), "PROVIDER_BLOCKED")
    require(set(data) == {"observations", "inferences", "goal", "obstacle", "steps", "clarification", "phase", "useful"}, "PROVIDER_BLOCKED")
    for key, maximum in (("observations", 6), ("inferences", 6), ("steps", 5)):
        require(isinstance(data[key], list) and len(data[key]) <= maximum, "PROVIDER_BLOCKED")
        data[key] = [string(item, 600, 1) for item in data[key]]
    for key in ("goal", "obstacle"):
        data[key] = string(data[key], 600)
    data["clarification"] = string(data["clarification"], 180)
    require(data["clarification"].count("?") <= 1, "PROVIDER_BLOCKED")
    require(data["phase"] in ("gameplay", "menu", "loading", "unknown") and type(data["useful"]) is bool, "PROVIDER_BLOCKED")
    require(has_image or not data["observations"], "PROVIDER_BLOCKED")
    labels = ("Visible", "Possible explanation", "Goal", "Obstacle", "Next steps") if language == "en" else (
        "Visibile", "Possibile spiegazione", "Obiettivo", "Ostacolo", "Prossimi passi")
    parts = []
    for key, label in zip(("observations", "inferences", "goal", "obstacle"), labels[:4], strict=True):
        content = "\n".join(data[key]) if isinstance(data[key], list) else data[key]
        if content:
            parts.append(label + ":\n" + content)
    if data["clarification"]:
        # A clarification and an invented solution must not compete.
        data["steps"] = []
        parts.append(data["clarification"])
    elif data["steps"]:
        parts.append(labels[4] + ":\n" + "\n".join(f"{i + 1}. {step}" for i, step in enumerate(data["steps"])))
    require(bool(parts), "PROVIDER_BLOCKED")
    return {"answer": "\n\n".join(parts), "situation": data}
