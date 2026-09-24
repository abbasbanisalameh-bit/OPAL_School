import json
import re
from pathlib import Path

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]


def source(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class ProductionCloseoutContractTests(SimpleTestCase):
    def test_release_identity_is_coherent_and_final_revision_is_monotonic(self):
        release_name = source("OPAL_RELEASE_NAME.txt").strip()
        manifest = json.loads(source("OPAL_UPDATE_MANIFEST.json"))
        self.assertEqual(source("OPAL_VERSION.txt").strip(), "131.7")
        self.assertEqual(manifest["version"], "131.7")
        self.assertEqual(manifest["version_name"], release_name)
        self.assertGreaterEqual(manifest["package_revision"], 13)
        self.assertIn(manifest.get("code_only"), (True, False))

    def test_primary_assets_share_the_final_nonempty_cache_token(self):
        tokens = re.findall(
            r"(?:opal_theme_system\.css|opal_theme_system\.css|opal_theme_system\.css|opal_erp\.js)' %\}\?v=([^\"\s]+)",
            source("templates/base/base.html"),
        )
        self.assertGreaterEqual(len(tokens), 2)
        self.assertEqual(len(set(tokens)), 1)
        self.assertTrue(all(token.strip() for token in tokens))

    def test_backup_recovery_report_reads_the_canonical_release_version(self):
        command = source("core/management/commands/audit_backup_recovery.py")
        self.assertIn('(root / "OPAL_VERSION.txt").read_text', command)
        self.assertNotIn('"version": "77"', command)

    def test_closeout_documents_are_present(self):
        # R9 is a historical closeout contract; retain the canonical checklist.
        relative = "OPAL_PRODUCTION_ENVIRONMENT_CHECKLIST_R9_AR.md"
        self.assertTrue((ROOT / relative).is_file(), relative)
