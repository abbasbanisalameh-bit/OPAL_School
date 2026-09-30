from pathlib import Path
import re

import tinycss2
from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "static/css/opal_theme_system.css"
RELEASE = "OPAL Update 131.7 R142 - Unified CSS Authority Re-engineering"
CACHE_TOKEN = "opal-131.7-r142-css-authority"


def _normalize_media_prelude(value):
    value = re.sub(r"\s+", " ", value.strip())
    value = re.sub(r"\s*:\s*", ":", value)
    value = re.sub(r"\s*,\s*", ",", value)
    return value


class R142CssAuthorityContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity(self):
        release = self.source("OPAL_RELEASE_NAME.txt").strip()
        manifest = self.source("OPAL_UPDATE_MANIFEST.json")
        self.assertEqual(release, RELEASE)
        self.assertIn('"package_revision": 144', manifest)
        self.assertIn('"baseline": "OPAL Update 131.7 R141 - Header Search Restore & Full Glass Table Alignment"', manifest)

    def test_css_parses_without_errors(self):
        rules = tinycss2.parse_stylesheet(CSS.read_text(encoding="utf-8"), skip_whitespace=True, skip_comments=True)
        self.assertFalse([r for r in rules if r.type == "error"])

    def test_top_level_selectors_are_unique(self):
        rules = tinycss2.parse_stylesheet(CSS.read_text(encoding="utf-8"), skip_whitespace=True, skip_comments=True)
        selectors = [tinycss2.serialize(r.prelude).strip() for r in rules if r.type == "qualified-rule"]
        duplicates = sorted({selector for selector in selectors if selectors.count(selector) > 1})
        self.assertEqual(duplicates, [], msg=f"duplicate top-level CSS selectors: {duplicates}")

    def test_media_blocks_and_selectors_are_unique(self):
        rules = tinycss2.parse_stylesheet(CSS.read_text(encoding="utf-8"), skip_whitespace=True, skip_comments=True)
        media_keys = []
        selector_property_duplicates = []
        for rule in rules:
            if rule.type != "at-rule" or rule.lower_at_keyword != "media" or rule.content is None:
                continue
            media_key = _normalize_media_prelude(tinycss2.serialize(rule.prelude))
            media_keys.append(media_key)
            nested = tinycss2.parse_rule_list(rule.content, skip_whitespace=True, skip_comments=True)
            selectors = [tinycss2.serialize(item.prelude).strip() for item in nested if item.type == "qualified-rule"]
            self.assertEqual(
                sorted({selector for selector in selectors if selectors.count(selector) > 1}),
                [],
                msg=f"duplicate selector inside {media_key}",
            )
            for item in nested:
                if item.type != "qualified-rule":
                    continue
                declarations = [
                    declaration.lower_name
                    for declaration in tinycss2.parse_declaration_list(item.content, skip_whitespace=True, skip_comments=True)
                    if declaration.type == "declaration"
                ]
                for name in {name for name in declarations if declarations.count(name) > 1}:
                    selector_property_duplicates.append((media_key, tinycss2.serialize(item.prelude).strip(), name))
        self.assertEqual(sorted({key for key in media_keys if media_keys.count(key) > 1}), [])
        self.assertEqual(selector_property_duplicates, [])

    def test_single_theme_token_authority(self):
        css = CSS.read_text(encoding="utf-8")
        self.assertEqual(css.count(":root {"), 1)
        self.assertEqual(css.count('html[data-opal-theme="green"] {'), 1)
        self.assertEqual(css.count('html[data-opal-theme="light"] {'), 1)
        self.assertNotIn("--opal-authority-", css)
        self.assertNotRegex(css, r"--opal-r\d+-")
        self.assertNotRegex(css, r"--opal-finish-")

    def test_all_local_css_links_use_r142_cache_token(self):
        for path in ROOT.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            if "opal_theme_system.css" in text:
                for link in re.findall(r"<link[^>]+rel=[\"']stylesheet[\"'][^>]*>", text, re.I | re.S):
                    if "static/css/opal_theme_system.css" in link:
                        self.assertIn(CACHE_TOKEN, link, msg=str(path))
        service_worker = self.source("templates/learning_platform/service-worker.js")
        self.assertIn(CACHE_TOKEN, service_worker)
