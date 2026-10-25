from pathlib import Path

from django.test import SimpleTestCase

from core.release_contract_assertions import assert_forward_compatible_release_identity

ROOT = Path(__file__).resolve().parents[1]


class R128TimetablePrintContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity_remains_forward_compatible(self):
        assert_forward_compatible_release_identity(self, self.source, min_revision=40)

    def test_timetable_uses_current_universal_scroll_authority(self):
        import re
        css = self.source("static/css/opal_theme_system.css")
        # R148/R152 superseded R128's old single-axis scrolling contract.
        compact = re.sub(r"\s+", "", css)
        for token in (
            ".opal-timetable-matrix-wrap.table-responsive",
            "overflow-x:auto!important;",
            "overflow-y:auto!important;",
            "touch-action:pan-xpan-y!important;",
            "direction:rtl;",
        ):
            self.assertIn(token, compact)

    def test_timetable_display_contracts_remain_canonical(self):
        templates = (
            "templates/timetable/overview.html",
            "templates/teachers/portal_timetable.html",
            "templates/teachers/portal_dashboard.html",
            "templates/teachers/teacher_detail.html",
            "templates/parent_portal/timetable.html",
            "templates/students/student_360.html",
        )
        for relative in templates:
            source = self.source(relative)
            self.assertIn("opal-timetable-grid", source, relative)
            self.assertIn("opal-timetable-matrix-wrap", source, relative)
            self.assertIn("opal-keep-grid", source, relative)

    def test_receipt_print_hardening_tokens_exist(self):
        import re
        css = self.source("static/css/opal_theme_system.css")
        # CSS whitespace is not semantic; normalize before checking declarations.
        compact = re.sub(r"\s+", "", css)
        for token in (
            "-webkit-text-fill-color:#111827!important;",
            "opacity:1!important;",
            "filter:none!important;",
            "mix-blend-mode:normal!important;",
            "forced-color-adjust:none!important;",
        ):
            self.assertIn(token, compact)

    def test_r128_cache_busting_is_applied(self):
        for relative in (
            "templates/base/base.html",
            "templates/admissions/registration_receipt.html",
            "templates/admissions/fee_payment_receipt.html",
            "templates/registration/auth_base.html",
            "templates/students/student_360_print.html",
        ):
            source = self.source(relative)
            self.assertRegex(source, r"opal-131\.7-r\d+-[a-z0-9-]+", relative)
            self.assertNotIn("opal-131.7-r127-theme-surface-print", source, relative)

    def test_single_css_authority_remains(self):
        css_files = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.css"))
        self.assertEqual(css_files, ["static/css/opal_theme_system.css"])
