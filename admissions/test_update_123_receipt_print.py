from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class ReceiptPrintUpdate123Tests(SimpleTestCase):
    def _template(self, name):
        return (Path(settings.BASE_DIR) / "templates" / "admissions" / name).read_text(encoding="utf-8")

    def _css(self):
        return (Path(settings.BASE_DIR) / "static" / "css" / "opal_theme_system.css").read_text(encoding="utf-8")

    def _assert_standalone_receipt(self, name):
        text = self._template(name)
        css = self._css()
        self.assertNotIn('{% extends "base/base.html" %}', text)
        self.assertIn("{% load static %}", text)
        self.assertIn("{% for copy_title in receipt_copies %}", text)
        self.assertIn("size:A4 landscape", css)
        self.assertIn("grid-template-columns:1fr 1fr", css)
        self.assertIn(".screen-toolbar", css)
        self.assertIn("display:none!important", css)
        self.assertIn("width:297mm", css)
        self.assertIn("height:210mm", css)

    def test_fee_receipt_is_standalone_two_copy_landscape_sheet(self):
        self._assert_standalone_receipt("fee_payment_receipt.html")

    def test_registration_receipt_is_standalone_two_copy_landscape_sheet(self):
        self._assert_standalone_receipt("registration_receipt.html")
