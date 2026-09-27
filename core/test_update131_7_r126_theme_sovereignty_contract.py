from pathlib import Path
import re
from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = ROOT / "static/css/opal_theme_system.css"


class R126ThemeSovereigntyContractTests(SimpleTestCase):
    def test_three_theme_tokens_bind_legacy_card_and_background_variables(self):
        css = CSS_PATH.read_text(encoding="utf-8")
        for theme in ("dark", "green", "light"):
            match = re.search(
                rf'html\[data-opal-theme="{theme}"\]\s*\{{(?P<body>.*?)\n\}}',
                css,
                re.S,
            )
            self.assertIsNotNone(match, theme)
            body = match.group("body")
            for token in ("--opal-card", "--opal-card-2", "--opal-r114-bg", "--opal-r114-border"):
                self.assertIn(token, body, f"{theme} missing {token}")

    def test_final_theme_sovereignty_layer_exists(self):
        css = CSS_PATH.read_text(encoding="utf-8")
        self.assertIn("OPAL Update 131.7 R126 — Theme Sovereignty Seal", css)
        self.assertIn("html[data-opal-theme] .opal-main :where(", css)
        self.assertIn(".opal-card,.card,.panel,.stat-card", css)
        self.assertIn("background:linear-gradient(145deg,var(--opal-card),var(--opal-card-2)) !important", css)

    def test_theme_layer_covers_settings_profile_and_student_360_surfaces(self):
        css = CSS_PATH.read_text(encoding="utf-8")
        for selector in (
            ".opal-settings-section",
            ".opal-settings-action",
            ".opal-inner-panel",
            ".opal-profile-preview",
            ".opal-entity-360 > .opal-card:first-child",
            ".opal-entity-360 .nav-pills",
            ".opal-compact-tabs .nav-link",
        ):
            self.assertIn(selector, css, selector)

    def test_theme_layer_keeps_print_background_white(self):
        css = CSS_PATH.read_text(encoding="utf-8")
        self.assertIn('@media print {\n  html[data-opal-theme] body {', css)
        self.assertIn('background:#fff !important;', css)

    def test_no_parallel_css_authority_was_added(self):
        css_files = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.css"))
        self.assertEqual(css_files, ["static/css/opal_theme_system.css"])
