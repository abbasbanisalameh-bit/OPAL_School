from pathlib import Path
from django.test import SimpleTestCase


class Update73FeedbackContractTests(SimpleTestCase):
    def test_feedback_styles_are_linked_once(self):
        root = Path(__file__).resolve().parents[1]
        base = (root / "templates" / "base" / "base.html").read_text(encoding="utf-8")
        self.assertEqual(base.count("opal_theme_system.css"), 1)
        self.assertRegex(base, r"opal-131.7-r[0-9]+-css-authority")

    def test_feedback_layer_covers_core_states(self):
        root = Path(__file__).resolve().parents[1]
        css = (root / "static" / "css" / "opal_theme_system.css").read_text(encoding="utf-8")
        for selector in (
            ".alert-success",
            ".alert-info",
            ".alert-warning",
            ".alert-danger",
            ".modal-content",
            ".toast",
            ".opal-empty-state",
        ):
            self.assertIn(selector, css)
