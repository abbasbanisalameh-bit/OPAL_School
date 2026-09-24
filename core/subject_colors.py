"""One display-level source of truth for OPAL subject colours."""
from __future__ import annotations

import hashlib
import re
from typing import Any

# Semantic colours are intentionally independent of the persisted Subject.color
# field. Existing database values remain for backward compatibility, while all
# user-facing subject displays use this deterministic map.
SEMANTIC_SUBJECT_COLORS = {
    "رياضيات": "#0B3A82",
    "الرياضيات": "#0B3A82",
    "math": "#0B3A82",
    "mathematics": "#0B3A82",
    "اللغة العربية": "#0E7490",
    "عربي": "#0E7490",
    "arabic": "#0E7490",
    "اللغة الإنجليزية": "#7C3AED",
    "إنجليزي": "#7C3AED",
    "انجليزي": "#7C3AED",
    "english": "#7C3AED",
    "العلوم": "#15803D",
    "علوم": "#15803D",
    "science": "#15803D",
    "فيزياء": "#9A3412",
    "physics": "#9A3412",
    "كيمياء": "#A21CAF",
    "chemistry": "#A21CAF",
    "أحياء": "#166534",
    "احياء": "#166534",
    "biology": "#166534",
    "الدراسات الاجتماعية": "#B45309",
    "اجتماعيات": "#B45309",
    "social studies": "#B45309",
    "التربية الإسلامية": "#7F1D1D",
    "تربية إسلامية": "#7F1D1D",
    "islamic education": "#7F1D1D",
    "الحاسوب": "#334155",
    "حاسوب": "#334155",
    "computer": "#334155",
    "التربية الرياضية": "#0369A1",
    "تربية رياضية": "#0369A1",
    "physical education": "#0369A1",
    "التربية الفنية": "#BE185D",
    "فنية": "#BE185D",
    "art": "#BE185D",
    "الموسيقى": "#64748B",
    "موسيقى": "#64748B",
    "music": "#64748B",
}

FALLBACK_PALETTE = (
    "#1D4ED8", "#0F766E", "#7C3AED", "#15803D", "#B45309",
    "#BE185D", "#334155", "#0369A1", "#7F1D1D", "#0E7490",
)


def _subject_name(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        name = value.get("name", "")
    else:
        name = getattr(value, "name", value)
    return str(name or "").strip().lower()


def canonical_subject_color(value: Any) -> str:
    """Return a deterministic fixed colour for a subject across all screens."""
    name = _subject_name(value)
    if not name:
        return "#64748B"

    colour = SEMANTIC_SUBJECT_COLORS.get(name)
    if colour:
        return colour

    token = name
    code = str((value.get("code", "") if isinstance(value, dict) else getattr(value, "code", "")) or "").strip().lower()
    if code:
        token = f"{code}:{name}"
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return FALLBACK_PALETTE[int(digest[:8], 16) % len(FALLBACK_PALETTE)]


_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def canonical_subject_color_from_value(value: Any) -> str:
    """Handle a raw subject name or an existing display object."""
    if hasattr(value, "name"):
        return canonical_subject_color(value)
    raw = str(value or "").strip()
    if _HEX.fullmatch(raw):
        return raw.upper()
    # Three-digit/invalid CSS colours are never accepted as display values.
    # Raw subject names still resolve through the canonical semantic map.
    if raw.startswith("#"):
        return "#64748B"
    return canonical_subject_color(raw)
