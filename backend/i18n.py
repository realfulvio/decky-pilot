import json
from pathlib import Path

LANGUAGES = ("en", "it")
ROOT = Path(__file__).resolve().parents[1] / "locales"
CATALOGS = {language: json.loads((ROOT / f"{language}.json").read_text(encoding="utf-8"))
            for language in LANGUAGES}


def translate(key, language="en"):
    return CATALOGS[language if language in LANGUAGES else "en"].get(
        key, CATALOGS["en"]["error.INTERNAL_ERROR"])
