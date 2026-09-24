"""Canonical subject-colour helpers shared by all OPAL templates."""
from __future__ import annotations

from typing import Any
import re

from django import template
from django.utils.html import format_html

from core.subject_colors import canonical_subject_color, canonical_subject_color_from_value

register = template.Library()


@register.simple_tag
def subject_style(subject: Any) -> str:
    return format_html("--opal-subject-color:{};", canonical_subject_color(subject))


_STRICT_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


@register.filter
def subject_colour(subject: Any) -> str:
    # Raw CSS values are accepted only as hexadecimal colours. Short three-digit
    # forms are expanded to six digits so the emitted value is always canonical.
    # Strings that look like executable/CSS payloads are never treated as subject
    # names; they resolve to the safe neutral fallback instead.
    if isinstance(subject, str):
        raw = subject.strip()
        if raw.startswith("#"):
            if _STRICT_HEX.fullmatch(raw):
                return raw.upper()
            if re.fullmatch(r"#[0-9A-Fa-f]{3}", raw):
                return "#" + "".join(ch * 2 for ch in raw[1:]).upper()
            return "#64748B"
        if re.search(r"(?i)^(?:javascript|vbscript|data):|[<>;{}()]|url\s*\(", raw):
            return "#64748B"
    return canonical_subject_color_from_value(subject)
