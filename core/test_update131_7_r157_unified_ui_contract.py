from pathlib import Path
import json

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[1]


class R157UnifiedUIContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_css_static_paths_do_not_embed_query_strings(self):
        for relative in (
            "templates/admissions/registration_receipt.html",
            "templates/admissions/fee_payment_receipt.html",
            "templates/parent_portal/guardian_receipt_print.html",
            "templates/registration/auth_base.html",
        ):
            source = self.source(relative)
            self.assertNotIn("static 'css/opal_theme_system.css?", source)
            self.assertRegex(source, r"\{% static 'css/opal_theme_system\.css' %\}\?v=opal-131\.7-r\d+-[a-z0-9-]+")

    def test_registration_receipt_retains_two_copy_print_contract(self):
        source = self.source("templates/admissions/registration_receipt.html")
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn("{% for copy_title in receipt_copies %}", source)
        self.assertIn("size:A4 landscape", css)
        self.assertRegex(css, r"width:\s*297mm\s*!important;")
        self.assertRegex(css, r"height:\s*210mm\s*!important;")

    def test_login_uses_shared_opal_authentication_template(self):
        source = self.source("templates/registration/login.html")
        auth = self.source("templates/registration/auth_base.html")
        self.assertIn('{% extends "registration/auth_base.html" %}', source)
        self.assertIn("{% csrf_token %}", source)
        self.assertIn("name=\"next\"", source)
        self.assertIn("opal-auth-page", auth)
        self.assertNotIn("OPAL_SCROLL_UNLOCKER", source)

    def test_logout_is_post_with_csrf_and_profile_has_one_action(self):
        profile = self.source("templates/accounts/my_profile.html")
        self.assertEqual(profile.count("opal-account-session-actions"), 1)
        for relative in ("templates/accounts/my_profile.html", "templates/includes/quick_access_modal.html"):
            source = self.source(relative)
            self.assertIn("{% url 'accounts:logout' %}", source)
            self.assertIn("{% csrf_token %}", source)
            self.assertIn('method="post"', source)

    def test_schedule_matrix_live_events_and_builder_share_one_canonical_screen(self):
        dashboard = self.source("templates/timetable/dashboard.html")
        catalog = self.source("core/workflow_catalog.py")
        urls = self.source("timetable/urls.py")
        self.assertIn("opal-live-events-matrix", dashboard)
        self.assertIn("opal-print-timetable", dashboard)
        self.assertIn('id="smart-builder"', dashboard)
        self.assertNotIn('"timetable:overview"', catalog)
        self.assertNotIn('"timetable-overview"', catalog)
        self.assertIn('name="overview"', urls)  # Legacy URL must redirect, not render a second page.
        self.assertFalse((ROOT / "templates/timetable/overview.html").exists())

    def test_auth_labels_are_readable_and_share_single_auth_template(self):
        auth = self.source("templates/registration/auth_base.html")
        css = self.source("static/css/opal_theme_system.css")
        login = self.source("templates/registration/login.html")
        self.assertIn('{% extends "registration/auth_base.html" %}', login)
        self.assertIn('class="opal-auth-document"', auth)
        self.assertIn(".opal-auth-shell label { color: #142746;", css)

    def test_generic_scroll_unlocker_is_not_reintroduced(self):
        for relative in (
            "templates/base/base.html",
            "templates/registration/auth_base.html",
            "templates/registration/login.html",
            "templates/admissions/registration_receipt.html",
            "templates/admissions/fee_payment_receipt.html",
            "templates/parent_portal/guardian_receipt_print.html",
        ):
            self.assertNotIn("OPAL_SCROLL_UNLOCKER", self.source(relative))

    def test_release_identity_matches_updater_invariant(self):
        version = self.source("OPAL_VERSION.txt").strip()
        release_name = self.source("OPAL_RELEASE_NAME.txt").strip()
        manifest = json.loads(self.source("OPAL_UPDATE_MANIFEST.json"))
        self.assertEqual(version, "131.7")
        self.assertEqual(manifest["version"], version)
        self.assertEqual(manifest["version_name"], release_name)
        self.assertEqual(manifest["package_revision"], 159)
        self.assertTrue(release_name.startswith("OPAL Update 131.7 R159 - "))

    def test_runtime_gate_requires_one_unified_timetable_screen(self):
        checks = self.source("core/checks.py")
        self.assertIn('"templates/timetable/dashboard.html"', checks)
        self.assertIn("TIMETABLE_UNIFIED_VIEW_INCOMPLETE", checks)
        self.assertIn("TIMETABLE_PARALLEL_TEMPLATE_PRESENT", checks)
    def test_single_entry_audit_matches_the_r157_navigation_contract(self):
        from core.single_entry_contracts import audit_role_gateways, audit_canonical_visible_entries
        self.assertEqual(audit_role_gateways(), [])
        self.assertEqual(audit_canonical_visible_entries(ROOT), [])

