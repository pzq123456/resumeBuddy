"""Safely edit one bullet in a resume JSON by stable id.

This is the only editing path the skill recommends. It cannot prevent other
tools from writing files; it makes the recommended path mechanical:

* target id must exist exactly once
* --expect must match the current text
* only the target text leaf may change
* --out must be a new file (never overwrite)

Usage (from the skill root):
    uv run scripts/edit.py <source.json> --id work.4s.b2 \
        --expect "old" --new "new" --lang en --out resumes/new.json
    uv run scripts/edit.py <source.json> --id work.4s.b2 \
        --expect "old" --remove --lang en --out resumes/new.json
"""
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

if __package__ in (None, ""):
    from resolve import localize
    from schema import ResumeValidationError, validate_raw
else:
    from .resolve import localize
    from .schema import ResumeValidationError, validate_raw


class EditError(ValueError):
    pass


def _entries(data: dict):
    for section in ("work", "projects"):
        entries = data.get(section, [])
        if not isinstance(entries, list):
            continue
        for ei, entry in enumerate(entries):
            if isinstance(entry, dict):
                yield section, ei, entry


def find_target(data: dict, target_id: str):
    """Return (section, entry_index, bullet_index, bullet) for one id."""
    matches = []
    for section, ei, entry in _entries(data):
        highlights = entry.get("highlights", [])
        if not isinstance(highlights, list):
            continue
        for hi, bullet in enumerate(highlights):
            if isinstance(bullet, dict) and bullet.get("id") == target_id:
                matches.append((section, ei, hi, bullet))
    if not matches:
        raise EditError(f"id not found: {target_id}")
    if len(matches) > 1:
        raise EditError(f"id is not unique: {target_id} ({len(matches)} matches)")
    return matches[0]


def _text(bullet: dict, lang: str | None) -> str:
    text = bullet.get("text")
    if isinstance(text, dict):
        if not lang:
            raise EditError("--lang is required for bilingual text")
        if lang not in text:
            raise EditError(f"text has no '{lang}' value")
        return text[lang]
    if not isinstance(text, str):
        raise EditError("bullet text must be a string or a bilingual object")
    return text


def _diff_paths(a, b, path=()):
    """Yield paths where two JSON values differ."""
    if type(a) is not type(b):
        yield path
        return
    if isinstance(a, dict):
        if set(a) != set(b):
            yield path
            return
        for key in a:
            yield from _diff_paths(a[key], b[key], path + (key,))
    elif isinstance(a, list):
        if len(a) != len(b):
            yield path
            return
        for i, (x, y) in enumerate(zip(a, b)):
            yield from _diff_paths(x, y, path + (i,))
    elif a != b:
        yield path


def apply_edit(data: dict, target_id: str, expect: str,
               new_text: str | None = None, lang: str | None = None,
               remove: bool = False) -> dict:
    """Return a deep-copied, edited document. Raises EditError on any risk."""
    if not remove and new_text is None:
        raise EditError("provide --new or --remove")
    if remove and new_text is not None:
        raise EditError("--new and --remove are mutually exclusive")

    edited = deepcopy(data)
    section, ei, hi, bullet = find_target(edited, target_id)
    current = _text(bullet, lang)
    if current != expect:
        raise EditError(
            f"{target_id}: --expect does not match current text\n"
            f"  expected: {expect!r}\n  current:  {current!r}")
    if not remove and new_text == current:
        raise EditError(f"{target_id}: --new is identical to current text")

    if remove:
        del edited[section][ei]["highlights"][hi]
        expected = deepcopy(data)
        target = find_target(expected, target_id)
        del expected[target[0]][target[1]]["highlights"][target[2]]
        if edited != expected:
            raise EditError("internal check failed: removed more than the target")
    else:
        text = bullet.get("text")
        if isinstance(text, dict):
            text[lang] = new_text
            allowed = (section, ei, "highlights", hi, "text", lang)
        else:
            bullet["text"] = new_text
            allowed = (section, ei, "highlights", hi, "text")
        diffs = list(_diff_paths(data, edited))
        if diffs != [allowed]:
            raise EditError(f"internal check failed: unexpected diff {diffs}")

    # Validate both languages so a broken fallback cannot slip through.
    for language in ("en", "zh"):
        try:
            validate_raw(localize(edited, language))
        except ResumeValidationError as exc:
            raise EditError(f"schema rejected the edited document: {exc}") from exc
    return edited


def _load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise EditError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise EditError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise EditError("root: expected object")
    return data


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Edit one bullet by stable id")
    p.add_argument("src")
    p.add_argument("--id", required=True, dest="target_id")
    p.add_argument("--expect", required=True)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--new")
    action.add_argument("--remove", action="store_true")
    p.add_argument("--lang", choices=("en", "zh"))
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)

    try:
        data = _load(Path(args.src))
        edited = apply_edit(
            data, args.target_id, args.expect,
            new_text=args.new, lang=args.lang, remove=args.remove,
        )
        out = Path(args.out)
        if out.exists():
            raise EditError(f"refusing to overwrite existing file: {out}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(edited, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    except EditError as exc:
        print(f"EditError: {exc}")
        return 2

    print(f"wrote {out}")
    print(f"{'removed' if args.remove else 'changed'} {args.target_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
