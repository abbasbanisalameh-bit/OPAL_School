import json
from pathlib import Path
from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[1]


class R144LuminousGlassContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity_advances_from_r143(self):
        release = self.source("OPAL_RELEASE_NAME.txt").strip()
        manifest = json.loads(self.source("OPAL_UPDATE_MANIFEST.json"))
        self.assertEqual(release, "OPAL Update 131.7 R144 - Luminous Glass System Theme")
        self.assertEqual(manifest["version_name"], release)
        self.assertEqual(manifest["baseline"], "OPAL Update 131.7 R143 - System UI Consistency & CSS Guard")
        self.assertEqual(manifest["package_revision"], 144)

    def test_luminous_glass_tokens_and_system_surfaces_exist(self):
        css = self.source("static/css/opal_theme_system.css")
        for marker in (
            "OPAL Update 131.7 R144 — Luminous Glass System Theme",
            "--opal-glass-accent: #53ddff",
            "--opal-glass-shadow",
            ".opal-sidebar",
            ".opal-card,",
            ".opal-topbar-shell",
            ".opal-global-search-box",
            ".opal-bottom-nav",
            "backdrop-filter:blur(22px)",
        ):
            self.assertIn(marker, css)

    def test_complex_tables_keep_horizontal_scroll_contract(self):
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn(".opal-mobile-scroll-table > table", css)
        self.assertIn("min-width:680px !important", css)
        self.assertIn("border-spacing:0 !important", css)

    def test_print_statement_stays_explicitly_outside_global_glass_theme(self):
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn("body.opal-standalone-opal_school_templates_parent_portal_family_statement_print_html", css)
        self.assertIn("background:#fff !important", css)
