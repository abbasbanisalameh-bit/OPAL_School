"""Contracts for OPAL Update 131.7 fixed manager dashboard."""

from pathlib import Path

from django.conf import settings


def _read(root: Path, relative: str) -> str:
    path = root / relative
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def run_fixed_dashboard_audit() -> dict[str, object]:
    root = Path(settings.BASE_DIR)
    issues: list[dict[str, str]] = []
    template = _read(root, "dashboard/templates/dashboard/home.html")
    views = _read(root, "dashboard/views.py")
    workflow = _read(root, "dashboard/workflow.py")
    css = _read(root, "static/css/opal_theme_system.css")

    required = {
        "dashboard/templates/dashboard/home.html": (
            "opal-reference-dashboard",
            "opal-dashboard-hero",
            "opal-dashboard-kpi-grid",
            "opal-dashboard-quick-grid",
            "opal-dashboard-feature-grid",
            "opal-dashboard-students-section",
            "opal-dashboard-more",
        ),
        "dashboard/views.py": (
            "@require_GET",
            "fixed canonical manager dashboard",
            "build_dashboard_context(request)",
        ),
        "dashboard/workflow.py": (
            'latest_enrollments = Enrollment.objects.filter(',
            "top_students_matrix",
            'row.get("rank") == 1',
        ),
        "static/css/opal_theme_system.css": (
            "OPAL R113 — reference dashboard visual system",
            ".opal-dashboard-kpi-grid",
            ".opal-dashboard-quick-grid",
            ".opal-dashboard-feature-grid",
            ".opal-dashboard-students-table",
            "border-style:solid !important",
        ),
    }
    retired = (
        "opal-dashboard-layout-form",
        "opal-dashboard-layout-data",
        "data-opal-layout-edit",
        "save_dashboard_layout",
        "reset_dashboard_layout",
        "user_dashboard_layout",
    )
    combined = template + "\n" + views
    if any(marker in combined for marker in retired):
        issues.append({"code": "DASHBOARD_CUSTOMIZER_STILL_ACTIVE", "message": "يجب حذف أداة تخصيص لوحة المدير ومسارات حفظها من التشغيل نهائيًا.", "path": "dashboard/templates/dashboard/home.html"})

    if (root / "static/js/opal_dashboard_layout.js").exists() or (root / "dashboard/layout.py").exists():
        issues.append({"code": "DASHBOARD_CUSTOMIZER_FILES_REMAIN", "message": "ملفات أداة التخصيص القديمة ما زالت ضمن الحزمة.", "path": "dashboard/"})

    order_markers = (
        "opal-dashboard-hero",
        "opal-dashboard-kpi-grid",
        "opal-dashboard-quick-grid",
        "opal-dashboard-feature-grid",
        "opal-dashboard-students-section",
        "opal-dashboard-more",
    )
    positions = [template.find(marker) for marker in order_markers]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        issues.append({"code": "FIXED_DASHBOARD_ORDER_MISMATCH", "message": "ترتيب عناصر لوحة المدير لا يطابق التسلسل التشغيلي المعتمد.", "path": "dashboard/templates/dashboard/home.html"})

    return {"ok": not issues, "issues": issues}
