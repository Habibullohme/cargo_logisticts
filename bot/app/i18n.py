"""Bot matnlari. Hozir faqat o'zbek lotin."""

import json
from functools import lru_cache
from pathlib import Path

DEFAULT_LOCALE = "uz_latn"
_LOCALES_DIR = Path(__file__).parent / "locales"


@lru_cache
def _load(locale: str) -> dict[str, str]:
    path = _LOCALES_DIR / f"{locale}.json"
    if not path.exists():
        path = _LOCALES_DIR / f"{DEFAULT_LOCALE}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def t(key: str, locale: str = DEFAULT_LOCALE, **params: object) -> str:
    text = _load(locale).get(key) or _load(DEFAULT_LOCALE).get(key) or key
    return text.format(**params) if params else text
