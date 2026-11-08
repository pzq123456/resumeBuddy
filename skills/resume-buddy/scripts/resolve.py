"""Source loading: read a resume JSON and collapse bilingual leaves.

The resume data is bilingual: a translatable leaf is either a plain string
(language-neutral, e.g. a tech name or a date) or ``{"en": ..., "zh": ...}``.

There is no inheritance or overlay layer. A tailored resume is a complete
snapshot of the base catalog; editing happens on that snapshot by stable ID.
Everything downstream (schema / normalize / renderer) consumes the localized
result, so it only ever sees plain strings.
"""
from __future__ import annotations

import json
from pathlib import Path

LANGS = ("en", "zh")


def is_localized(value) -> bool:
    """True for a ``{"en": str, "zh": str}`` leaf (at least one string)."""
    if not isinstance(value, dict) or not value:
        return False
    if not set(value).issubset(LANGS):
        return False
    return any(isinstance(value.get(k), str) for k in LANGS)


def pick(value, lang: str):
    """Resolve a localized leaf to ``lang`` (falling back to the other)."""
    if is_localized(value):
        return value.get(lang) or value.get("en") or value.get("zh") or ""
    return value


def localize(value, lang: str):
    """Recursively collapse every localized leaf to the chosen language."""
    if is_localized(value):
        return pick(value, lang)
    if isinstance(value, dict):
        return {k: localize(v, lang) for k, v in value.items()}
    if isinstance(value, list):
        return [localize(v, lang) for v in value]
    return value


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_source(src_path: Path, lang: str | None = None) -> dict:
    """Load ``src_path`` and optionally localize it to ``lang``.

    ``lang=None`` keeps the bilingual structure (used by tools that edit the
    source directly, such as ``edit.py``).
    """
    raw = load_json(src_path)
    return raw if lang is None else localize(raw, lang)
