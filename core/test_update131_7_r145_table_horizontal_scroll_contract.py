import json
from pathlib import Path

from django.test import SimpleTestCase
import tinycss2

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "static/css/opal_theme_system.css"
RELEASE = "OPAL Update 131.7 R145 - Global Table Horizontal Scroll Authority"
BASELINE = "OPAL Update 131.7 R145 - Unified Tables, Horizontal Scroll & Centered Bottom Navigation"
CACHE_TOKEN = "opal-131.7-r145-table-horizontal-authority"


class R145TableHorizontalScrollContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity(self):
        release = self.source("OPAL_RELEASE_NAME.txt").strip()
        manifest = json.loads(self.source("OPAL_UPDATE_MANIFEST.json"))
        self.assertEqual(release, RELEASE)
        self.assertEqual(manifest["version_name"], release)
        self.assertEqual(manifest["package_revision"], 145)
        self.assertEqual(manifest["baseline"], BASELINE)

    def test_css_parses_without_errors(self):
        rules = tinycss2.parse_stylesheet(CSS.read_text(encoding="utf-8"), skip_whitespace=True, skip_comments=True)
        self.assertFalse([rule for rule in rules if rule.type == "error"])

    def test_single_shared_css_file_contracts(self):
        css = CSS.read_text(encoding="utf-8")
        rules = tinycss2.parse_stylesheet(css, skip_whitespace=True, skip_comments=True)
        top_level_root = [r for r in rules if r.type == "qualified-rule" and tinycss2.serialize(r.prelude).strip() == ":root"]
        top_level_green = [r for r in rules if r.type == "qualified-rule" and tinycss2.serialize(r.prelude).strip() == 'html[data-opal-theme="green"]']
        top_level_light = [r for r in rules if r.type == "qualified-rule" and tinycss2.serialize(r.prelude).strip() == 'html[data-opal-theme="light"]']
        self.assertEqual(len(top_level_root), 1)
        self.assertEqual(len(top_level_green), 1)
        self.assertEqual(len(top_level_light), 1)
        self.assertIn("OPAL Update 131.7 R145", css)
        self.assertIn("width: max-content", css)
        self.assertIn("white-space: nowrap", css)
        self.assertIn("left: 50%", css)
        self.assertIn("translateX(-50%)", css)

    def test_cache_busting_uses_r145(self):
        for relative in ("templates/base/base.html", "templates/parent_portal/family_statement_print.html"):
            self.assertIn(CACHE_TOKEN, self.source(relative), msg=relative)

    def test_previous_r143_update_center_contracts_remain(self):
        template = self.source("templates/core/system_updates.html")
        console = self.source("templates/core/system_console.html")
        self.assertIn('data-update-source="local"', template)
        self.assertIn('data-update-source="github"', template)
        self.assertIn("open_system_console", template)
        self.assertIn("opal-console-close", console)

    def test_bottom_nav_has_centered_mobile_contract(self):
        css = CSS.read_text(encoding="utf-8")
        self.assertIn("left: 50% !important", css)
        self.assertIn("width: min(540px, calc(100vw - 20px)) !important", css)
        self.assertIn("transform: translateX(-50%) !important", css)

    def test_standard_tables_have_horizontal_scroll_contract(self):
        css = CSS.read_text(encoding="utf-8")
        self.assertIn("overflow-x: auto !important", css)
        self.assertIn("min-width: max-content !important", css)
        self.assertIn("max-width: none !important", css)
        self.assertIn("width: max-content !important", css)
        self.assertIn("white-space: nowrap !important", css)
        self.assertIn(":not(.opal-mobile-card-table)", css)
