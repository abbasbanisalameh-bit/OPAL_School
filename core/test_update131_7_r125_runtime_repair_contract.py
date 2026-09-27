from pathlib import Path
from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]


class R125RuntimeRepairContractTests(SimpleTestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_receipt_templates_are_static_safe_standalone_pages(self):
        for name in ("registration_receipt.html", "fee_payment_receipt.html"):
            text = self.read(f"templates/admissions/{name}")
            self.assertTrue(text.startswith("{% load static %}"), name)
            self.assertNotIn("<style", text.lower(), name)
            self.assertIn("{% for copy_title in receipt_copies %}", text, name)

    def test_receipt_and_student_print_styles_live_in_the_authority_css(self):
        css = self.read("static/css/opal_theme_system.css")
        for token in (
            ".opal-standalone-opal_school_templates_admissions_registration_receipt_html .receipt-sheet",
            ".opal-standalone-opal_school_templates_admissions_fee_payment_receipt_html .receipt-sheet",
            ".opal-standalone-opal_school_templates_students_student_360_print_html .head",
            "@page opal-receipt-landscape",
            "size:A4 landscape",
        ):
            self.assertIn(token, css)

    def test_student360_uses_registration_receipt_label(self):
        text = self.read("templates/students/student_360.html")
        self.assertIn("إيصال التسجيل", text)
        self.assertNotIn("سجل التسجيل</a>", text)

    def test_historical_startup_contract_markers_remain_after_css_consolidation(self):
        css = self.read("static/css/opal_theme_system.css")
        for token in (
            "OPAL Update 130: production timetable state and mobile containment",
            "OPAL Update 131: consolidated timetable states and print contract",
            "OPAL Update 131.4: live grade/section event matrix",
            ".opal-timetable-entry.is-current",
            "width: min(86dvw, 330px) !important",
            ".opal-live-events-matrix .opal-live-axis-cell",
        ):
            self.assertIn(token, css)
