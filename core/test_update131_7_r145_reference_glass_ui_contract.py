import json
from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[1]


class R145ReferenceGlassUIContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity_advances_from_r144(self):
        release = self.source("OPAL_RELEASE_NAME.txt").strip()
        manifest = json.loads(self.source("OPAL_UPDATE_MANIFEST.json"))
        self.assertEqual(release, "OPAL Update 131.7 R145 - Reference Glass UI, Search Simplification & Mobile Layout Repair")
        self.assertEqual(manifest["version_name"], release)
        self.assertEqual(manifest["baseline"], "OPAL Update 131.7 R144 - Luminous Glass System Theme")
        self.assertEqual(manifest["package_revision"], 145)

    def test_reference_glass_overrides_legacy_profile_surfaces(self):
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn('html[data-opal-theme="dark"] .opal-main :where(', css)
        self.assertIn('.opal-entity-360 > .opal-card:first-child', css)
        self.assertIn('.opal-teacher-360 > .d-flex:first-child', css)
        self.assertIn('backdrop-filter:blur(24px) saturate(150%) !important', css)

    def test_mobile_teacher_profile_stacks_columns(self):
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn('.opal-teacher-360 > .row.g-3.mb-4', css)
        self.assertIn('flex-direction:column !important;', css)
        self.assertIn('flex:0 0 100% !important;', css)

    def test_student_list_has_no_duplicate_free_text_search(self):
        template = self.source("templates/students/student_list.html")
        self.assertNotIn('name="q"', template)
        self.assertIn('data-live-filter="change"', template)
        view = self.source("students/views.py")
        self.assertNotIn('request.GET.get("q"', view)

    def test_instant_table_search_remains(self):
        js = self.source("static/js/opal_erp.js")
        self.assertIn('بحث فوري داخل الجدول', js)
        self.assertIn('table.opal-table', js)

    def test_only_one_css_authority_remains(self):
        css_files = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.css"))
        self.assertEqual(css_files, ["static/css/opal_theme_system.css"])
