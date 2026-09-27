from pathlib import Path

from django.test import SimpleTestCase

from core.release_contract_assertions import assert_forward_compatible_release_identity

ROOT = Path(__file__).resolve().parents[1]


class R129ReceiptContentContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity_remains_forward_compatible(self):
        assert_forward_compatible_release_identity(self, self.source, min_revision=41)

    def test_receipts_are_explicitly_visible(self):
        css = self.source("static/css/opal_theme_system.css")
        for token in (
            "visibility:visible !important;",
            "opacity:1 !important;",
            "-webkit-text-fill-color:#111827 !important;",
            "position:relative !important;",
            "inset:auto !important;",
            "overflow:visible !important;",
        ):
            self.assertIn(token, css)

    def test_receipt_print_surface_uses_normal_flow(self):
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn("width:297mm !important;", css)
        self.assertIn("height:210mm !important;", css)
        self.assertIn("height:198mm !important;", css)
        self.assertIn("grid-template-columns:1fr 1fr !important;", css)

    def test_receipt_templates_keep_server_rendered_context(self):
        for relative in (
            "templates/admissions/registration_receipt.html",
            "templates/admissions/fee_payment_receipt.html",
        ):
            source = self.source(relative)
            self.assertIn("{% load static %}", source)
            self.assertIn("{% for copy_title in receipt_copies %}", source)
            self.assertNotIn("{% extends", source)
