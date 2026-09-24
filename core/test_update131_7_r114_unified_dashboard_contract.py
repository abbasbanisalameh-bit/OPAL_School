from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parent.parent

class Update1317R114UnifiedDashboardContractTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity_is_coherent(self):
        manifest = json.loads(self.read("OPAL_UPDATE_MANIFEST.json"))
        release = self.read("OPAL_RELEASE_NAME.txt").strip()
        self.assertEqual(manifest["version"], "131.7")
        self.assertEqual(manifest["package_revision"], 114)
        self.assertEqual(manifest["version_name"], release)
        self.assertFalse(manifest["code_only"])
        self.assertTrue(manifest["database_changes"])
        self.assertTrue(manifest["model_changes"])
        self.assertTrue(manifest["migration_changes"])

    def test_sidebar_is_not_rendered(self):
        base = self.read("templates/base/base.html")
        topbar = self.read("templates/includes/topbar.html")
        self.assertNotIn('{% include "includes/sidebar.html" %}', base)
        self.assertNotIn("opal-sidebar-toggle", topbar)
        self.assertIn("opal-quick-access-trigger", topbar)
        self.assertIn('{% include "includes/bottom_nav.html" %}', base)
        self.assertIn('{% include "includes/quick_access_modal.html" %}', base)
        self.assertIn("{% url 'dashboard:home' %}", self.read("templates/includes/bottom_nav.html"))

    def test_dashboard_uses_quick_access_and_keeps_evaluation_system(self):
        dashboard = self.read("dashboard/templates/dashboard/home.html")
        self.assertIn("opal-dashboard-quick-grid", dashboard)
        self.assertIn("كل بوابات النظام في مكان واحد", dashboard)
        self.assertNotIn("teacher_evaluation_chart", dashboard)

    def test_single_css_authority(self):
        base = self.read("templates/base/base.html")
        self.assertEqual(base.count("css/opal_theme_system.css"), 1)

if __name__ == "__main__":
    unittest.main()
