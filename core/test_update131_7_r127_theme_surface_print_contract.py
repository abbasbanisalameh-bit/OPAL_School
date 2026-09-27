from pathlib import Path

from django.test import SimpleTestCase

from core.release_contract_assertions import assert_forward_compatible_release_identity

ROOT = Path(__file__).resolve().parents[1]


class R127ThemeSurfacePrintContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity_remains_forward_compatible(self):
        assert_forward_compatible_release_identity(self, self.source, min_revision=39)

    def test_dashboard_surfaces_are_theme_owned(self):
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn("OPAL Update 131.7 R127 — Theme Surface & Print Legibility Repair", css)
        for selector in (
            ".opal-dashboard-section", ".opal-dashboard-feature",
            ".opal-dashboard-more", ".opal-dashboard-mini-panel",
            ".opal-dashboard-students-wrap",
        ):
            self.assertIn(selector, css)
        self.assertIn("background:linear-gradient(145deg,var(--opal-card),var(--opal-card-2)) !important", css)

    def test_receipts_are_theme_independent_and_print_legible(self):
        css = self.source("static/css/opal_theme_system.css")
        for selector in (
            "body.opal-standalone-opal_school_templates_admissions_registration_receipt_html",
            "body.opal-standalone-opal_school_templates_admissions_fee_payment_receipt_html",
        ):
            self.assertIn(selector, css)
        self.assertIn("background:#fff !important;", css)
        self.assertIn("color:#111827 !important;", css)

    def test_receipt_templates_keep_central_css_only(self):
        for rel in (
            "templates/admissions/registration_receipt.html",
            "templates/admissions/fee_payment_receipt.html",
        ):
            html = self.source(rel)
            self.assertIn("{% load static %}", html)
            self.assertNotIn("<style", html.lower())
            self.assertRegex(html, r"opal-131\.7-r\d+-[a-z0-9-]+")

    def test_single_css_authority_remains(self):
        css_files = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.css"))
        self.assertEqual(css_files, ["static/css/opal_theme_system.css"])
