from pathlib import Path
import re
from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]


class R124SingleCssAuthorityContractTests(SimpleTestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_only_one_opal_css_file_exists(self):
        css_files = sorted((ROOT / "static" / "css").glob("*.css"))
        self.assertEqual([p.name for p in css_files], ["opal_theme_system.css"])

    def test_base_has_no_extra_css_escape_hatch(self):
        base = self.read("templates/base/base.html")
        self.assertNotIn("block extra_css", base)
        self.assertEqual(base.count("css/opal_theme_system.css"), 1)

    def test_theme_is_loaded_by_auth_base(self):
        auth = self.read("templates/registration/auth_base.html")
        self.assertEqual(auth.count("css/opal_theme_system.css"), 1)

    def test_no_template_style_blocks_remain(self):
        for path in (ROOT / "templates").rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"<style\b", msg=str(path))

    def test_static_inline_color_styles_are_not_allowed(self):
        for path in (ROOT / "templates").rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r'\bstyle\s*=\s*([\'"])(.*?)\1', text, re.I | re.S):
                value = match.group(2)
                if "{{" not in value and "{%" not in value and "${" not in value:
                    self.assertNotRegex(
                        value,
                        r"(?i)\b(color|background|background-color|border|box-shadow|fill|stroke)\s*:",
                        msg=f"static visual inline style in {path}: {value}",
                    )

    def test_satisfaction_ring_uses_theme_variables_for_inner_value(self):
        css = self.read("static/css/opal_theme_system.css")
        self.assertIn("--opal-satisfaction-inner:var(--opal-surface)", css)
        self.assertIn(".opal-satisfaction-ring span", css)
        self.assertIn("color:var(--opal-text)!important", css)
        self.assertIn("R124 — SINGLE CSS AUTHORITY", css)
