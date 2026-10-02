import json
from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[1]


class R146CssAuthorityContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity_advances_from_r145(self):
        release = self.source("OPAL_RELEASE_NAME.txt").strip()
        manifest = json.loads(self.source("OPAL_UPDATE_MANIFEST.json"))
        self.assertEqual(
            release,
            "OPAL Update 131.7 R146 - Clean CSS Authority & Glass System Consolidation",
        )
        self.assertEqual(manifest["version_name"], release)
        self.assertEqual(
            manifest["baseline"],
            "OPAL Update 131.7 R145 - Reference Glass UI, Search Simplification & Mobile Layout Repair",
        )
        self.assertEqual(manifest["package_revision"], 146)

    def test_one_css_authority_and_no_parallel_opal_stylesheet(self):
        css_files = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.css"))
        self.assertEqual(css_files, ["static/css/opal_theme_system.css"])
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn("@layer opal-foundation", css)
        self.assertIn("OPAL Update 131.7 R146 — CLEAN CSS AUTHORITY", css)
        self.assertNotIn("OPAL Update 131.7 R144 — Luminous Glass System Theme", css)
        self.assertNotIn("OPAL Update 131.7 R145 — Reference Glass UI", css)

    def test_reference_palette_is_canonical(self):
        css = self.source("static/css/opal_theme_system.css")
        for marker in (
            "--opal-glass-bg: rgba(7, 34, 61, .58);",
            "--opal-glass-bg-strong: rgba(8, 42, 74, .78);",
            "--opal-glass-accent: #53ddff;",
            "--opal-glass-shadow: 0 18px 48px rgba(0, 8, 28, .30);",
            ".opal-topbar-shell",
            ".opal-global-search-box",
            ".opal-bottom-nav",
        ):
            self.assertIn(marker, css)

    def test_tables_have_one_continuous_contract_and_wide_matrices_remain_scrollable(self):
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn("border-spacing:0 !important", css)
        self.assertIn(".opal-mobile-scroll-table > table", css)
        self.assertIn("min-width:680px !important", css)

    def test_instant_table_search_remains_and_student_free_text_search_stays_removed(self):
        js = self.source("static/js/opal_erp.js")
        template = self.source("templates/students/student_list.html")
        self.assertIn("بحث فوري داخل الجدول", js)
        self.assertIn("table.opal-table", js)
        self.assertNotIn('name="q"', template)
        self.assertNotIn('request.GET.get("q"', self.source("students/views.py"))

    def test_mobile_teacher_profile_stacks(self):
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn(".opal-teacher-360 > .row.g-3.mb-4", css)
        self.assertIn("flex-direction:column !important;", css)
        self.assertIn("flex:0 0 100% !important;", css)
