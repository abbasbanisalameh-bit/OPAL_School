from pathlib import Path
import re

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_TEMPLATE = ROOT / "dashboard" / "templates" / "dashboard" / "home.html"
EXECUTIVE_CSS = ROOT / "static" / "css" / "opal_theme_system.css"
POLISH_CSS = ROOT / "static" / "css" / "opal_theme_system.css"
BASE_TEMPLATE = ROOT / "templates" / "base" / "base.html"


class Update116ExecutiveDashboardContractTests(SimpleTestCase):
    def test_reference_dashboard_has_four_kpis(self):
        source = DASHBOARD_TEMPLATE.read_text(encoding="utf-8")
        kpi_source = source[source.index("opal-dashboard-kpi-grid"):source.index("</section>", source.index("opal-dashboard-kpi-grid"))]
        anchors = re.findall(r'<a\b[^>]*class="[^"]*\bopal-dashboard-kpi\b[^"]*"[^>]*>', kpi_source)
        self.assertEqual(len(anchors), 4)

    def test_reference_dashboard_order_is_explicit(self):
        source = DASHBOARD_TEMPLATE.read_text(encoding="utf-8")
        positions = [
            source.index("opal-dashboard-hero"),
            source.index("opal-dashboard-kpi-grid"),
            source.index("opal-dashboard-quick-grid"),
            source.index("opal-dashboard-feature-grid"),
            source.index("opal-dashboard-students-section"),
            source.index("opal-dashboard-more"),
        ]
        self.assertEqual(positions, sorted(positions))

    def test_reference_kpis_have_distinct_visual_classes(self):
        source = EXECUTIVE_CSS.read_text(encoding="utf-8")
        self.assertIn("grid-template-columns:repeat(4,minmax(0,1fr))", source)
        for name in (
            "opal-dashboard-kpi",
            "kpi-students",
            "kpi-teachers",
            "kpi-attendance",
            "kpi-fees",
        ):
            self.assertIn(f".{name}", source)

    def test_announcement_uses_gold_text_and_multicolour_icon_only(self):
        source = POLISH_CSS.read_text(encoding="utf-8")
        self.assertIn("OPAL Update 116 — announcement text only in gold", source)
        self.assertIn("color:#e7bd54!important", source)
        self.assertIn("linear-gradient(135deg,#38bdf8", source)
        self.assertNotIn(".opal-topbar-ribbon{background:linear-gradient", source)

    def test_static_cache_keys_point_to_update_116(self):
        source = BASE_TEMPLATE.read_text(encoding="utf-8")
        self.assertRegex(source, r"opal_theme_system\.css' %\}\?v=[^\"\s]+")
        self.assertRegex(source, r"opal_theme_system\.css' %\}\?v=[^\"\s]+")
