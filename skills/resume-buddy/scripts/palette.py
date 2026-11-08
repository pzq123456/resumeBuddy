"""Accent palette helpers (stdlib only).

The renderer has one layout and one user-supplied accent color. These helpers
compute the few derived shades explicitly in Python (no CSS color-mix), so
print/PDF output is stable across Chromium versions.
"""
from __future__ import annotations


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def mix(hex_a: str, hex_b: str, pct_a: float) -> str:
    """Mix two hex colors; pct_a = share of color A (0..1)."""
    ar, ag, ab = _hex_to_rgb(hex_a)
    br, bg, bb = _hex_to_rgb(hex_b)
    m = lambda a, b: round(pct_a * a + (1 - pct_a) * b)
    return _rgb_to_hex(m(ar, br), m(ag, bg), m(ab, bb))


def mix_white(hex_color: str, pct: float) -> str:
    return mix(hex_color, "#FFFFFF", pct)


def accent_palette(accent: str = "#B14E2E") -> dict:
    """Return the accent and its explicit derived shades."""
    accent = accent.strip()
    ink = "#20242A"
    return {
        "base": accent,
        "soft": mix(accent, ink, 0.72),
        "wash": mix_white(accent, 0.10),
        "pale": mix_white(accent, 0.09),
    }
