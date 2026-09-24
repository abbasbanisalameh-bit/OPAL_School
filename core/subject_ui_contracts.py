"""Behavioral contracts for OPAL Update 131.6 subject colours and compact gateways."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings


def _read(root: Path, relative: str) -> str:
    path = root / relative
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def run_subject_ui_audit() -> dict[str, object]:
    root = Path(settings.BASE_DIR)
    issues: list[dict[str, str]] = []

    required = {
        "core/templatetags/opal_subjects.py": (
            "subject_style", "subject_colour",
        ),
        "static/css/opal_theme_system.css": (
            ".opal-subject-chip", ".opal-subject-card",
            ".opal-compact-module-grid", ".opal-compact-action-row",
            "grid-template-columns:repeat(3,minmax(0,1fr))!important",
            ".opal-reference-dashboard", ".opal-dashboard-quick-grid",
        ),
        "templates/base/base.html": ("css/opal_theme_system.css",),
        "timetable/live_services.py": (
            "canonical_subject_color(entry.subject)", '"subject_color": subject_color',
        ),
        # The R113 reference dashboard intentionally has no subject matrix;
        # subject colours remain owned by subject/teacher/student/exam views.

        "templates/teachers/portal_dashboard.html": (
            "opal-compact-module-grid", "opal-compact-subject-grid", "subject_style a.subject",
        ),
        "templates/parent_portal/dashboard.html": (
            "opal-parent-metric-grid", "opal-compact-module-grid",
        ),
        "templates/students/student_360.html": (
            "opal-compact-action-row", "opal-compact-metric-grid",
            "opal-compact-tabs", "subject_style row.exam.subject",
        ),
        "templates/exams/gradebook.html": (
            "opal-subject-card", "subject_style mark.exam.subject",
        ),
    }

    for relative, markers in required.items():
        source = _read(root, relative)
        if not source:
            issues.append({
                "code": "SUBJECT_UI_FILE_MISSING",
                "message": "ملف توحيد ألوان المواد أو البطاقات المصغرة غير موجود.",
                "path": relative,
            })
            continue
        missing = [marker for marker in markers if marker not in source]
        if missing:
            issues.append({
                "code": "SUBJECT_UI_CONTRACT_MISSING",
                "message": "تطبيق ألوان المواد أو البطاقات المصغرة غير مكتمل: " + "، ".join(missing),
                "path": relative,
            })

    # Exercise the colour normalizer instead of relying only on exact source text.
    try:
        from core.templatetags.opal_subjects import subject_colour

        safe = (
            subject_colour("#12abEF") == "#12ABEF"
            and subject_colour("javascript:alert(1)") == "#64748B"
            and subject_colour("#fff") == "#FFFFFF"
            and subject_colour("#FFFFFF") == "#FFFFFF"
            and subject_colour("#12345") == "#64748B"
        )
    except Exception:
        safe = False
    if not safe:
        issues.append({
            "code": "SUBJECT_COLOUR_VALIDATION_WEAK",
            "message": "مساعد لون المادة لا يقيد القيم إلى لون سداسي آمن.",
            "path": "core/templatetags/opal_subjects.py",
        })

    return {"ok": not issues, "issues": issues}
