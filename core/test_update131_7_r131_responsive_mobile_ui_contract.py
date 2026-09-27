from pathlib import Path

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]


class R131ResponsiveMobileUiContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity(self):
        release = self.source("OPAL_RELEASE_NAME.txt").strip()
        manifest = self.source("OPAL_UPDATE_MANIFEST.json")
        self.assertEqual(release, "OPAL Update 131.7 R131 - Responsive Viewport & Mobile Navigation Polish")
        self.assertIn('"package_revision": 43', manifest)
        self.assertIn('"code_only": true', manifest)

    def test_bottom_nav_has_five_stable_actions_and_top_inside_bar(self):
        nav = self.source("templates/includes/bottom_nav.html")
        self.assertEqual(nav.count("<a ") + nav.count("<button "), 5)
        self.assertIn('id="opal-scroll-top"', nav)
        self.assertIn('data-opal-bottom-link="home"', nav)
        self.assertIn('data-opal-bottom-link="profile"', nav)

    def test_quick_access_keeps_settings_and_profile_available(self):
        modal = self.source("templates/includes/quick_access_modal.html")
        self.assertNotIn('item.key != "system-settings"', modal)
        self.assertNotIn('item.key != "profile"', modal)

    def test_responsive_contract_and_selected_card_glow(self):
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn("--opal-r131-content-max: 1320px", css)
        self.assertIn("width: 100%;", css)
        self.assertIn(".opal-clickable-card.is-selected", css)
        self.assertIn(".opal-bottom-nav .opal-bottom-scroll-top", css)
        self.assertIn("overscroll-behavior-inline: contain", css)

    def test_cache_version_is_advanced(self):
        base = self.source("templates/base/base.html")
        self.assertIn("opal-131.7-r131-responsive-mobile-ui", base)
