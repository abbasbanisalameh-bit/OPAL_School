from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class R158LiveRefreshGuardContractTests(unittest.TestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_live_refresh_ignores_zero_and_expired_boundaries(self):
        js = self.source("static/js/opal_erp.js")
        self.assertIn("function installLiveBoundaryRefresh()", js)
        self.assertIn("Number.isFinite(value) && value > 0", js)
        self.assertIn("opal-event-countdown", js)
        self.assertIn("if (!futureBoundaries.length) return;", js)

    def test_timetable_overview_has_no_duplicate_refresh_timer(self):
        page = self.source("templates/timetable/overview.html")
        self.assertIn("Live-boundary refresh is handled once", page)
        self.assertNotIn("window.location.reload()", page)

    def test_topbar_countdown_does_not_reload_forever_at_zero(self):
        base = self.source("templates/base/base.html")
        self.assertIn("if(s<=0)return;", base)
        self.assertIn("window.clearInterval(timer)", base)
        self.assertNotIn("else window.location.reload()", base)

    def test_release_identity_is_sequential_and_compatible(self):
        import json
        manifest = json.loads(self.source("OPAL_UPDATE_MANIFEST.json"))
        self.assertEqual(manifest["version"], "131.7")
        self.assertEqual(manifest["package_revision"], 158)
        self.assertEqual(self.source("OPAL_VERSION.txt").strip(), "131.7")
        self.assertEqual(self.source("OPAL_RELEASE_NAME.txt").strip(), manifest["version_name"])


if __name__ == "__main__":
    unittest.main()
