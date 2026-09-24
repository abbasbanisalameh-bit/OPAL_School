from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parent.parent


class Update1317R113DashboardContractTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity_is_current_and_coherent(self):
        manifest = json.loads(self.read("OPAL_UPDATE_MANIFEST.json"))
        release = self.read("OPAL_RELEASE_NAME.txt").strip()
        self.assertEqual(manifest["version"], "131.7")
        self.assertEqual(manifest["package_revision"], 114)
        self.assertEqual(manifest["version_name"], release)
        self.assertTrue(release.startswith("OPAL Update 131.7 R114 - "))

    def test_dashboard_matches_reference_structure(self):
        source = self.read("dashboard/templates/dashboard/home.html")
        for marker in (
            "opal-reference-dashboard",
            "opal-dashboard-hero",
            "opal-dashboard-kpi-grid",
            "opal-dashboard-quick-grid",
            "opal-dashboard-feature-grid",
            "opal-dashboard-students-section",
        ):
            self.assertIn(marker, source)
        self.assertEqual(source.count("opal-dashboard-kpi "), 4)

    def test_settings_does_not_duplicate_daily_grade_section_management(self):
        source = self.read("templates/core/system_settings.html")
        section = source.split('id="grades-sections-setup"', 1)[1].split('</section>', 1)[0]
        self.assertNotIn("academics:academic_structure", section)
        self.assertIn("تُدار من بوابة الصفوف والشعب", section)

    def test_mobile_readability_contract(self):
        css = self.read("static/css/opal_theme_system.css")
        self.assertIn("OPAL R113 — reference dashboard visual system", css)
        self.assertIn("font-size:.78rem !important", css)
        self.assertIn("min-height:92px !important", css)
        self.assertIn("border-style:solid !important", css)

    def test_full_code_download_action_exists(self):
        view = self.read("core/system_update_views.py")
        template = self.read("templates/core/system_updates.html")
        self.assertIn('action == "download_current_snapshot"', view)
        self.assertIn('action" value="download_current_snapshot"', template)
        self.assertIn("تحميل النظام بالكامل (الكود)", template)


if __name__ == "__main__":
    unittest.main()
