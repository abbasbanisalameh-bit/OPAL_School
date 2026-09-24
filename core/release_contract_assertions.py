from __future__ import annotations

import json
import re
from collections.abc import Callable


def assert_forward_compatible_release_identity(
    test_case,
    source: Callable[[str], str],
    *,
    min_revision: int,
) -> None:
    """Validate the installed 131.7 release without pinning a historical revision.

    Historical feature contracts remain executable after later revisions.  The
    current release identity is authoritative in OPAL_RELEASE_NAME.txt and the
    manifest, while each historical contract only enforces its minimum package
    revision.
    """

    version = source("OPAL_VERSION.txt").strip()
    release_name = source("OPAL_RELEASE_NAME.txt").strip()
    manifest = json.loads(source("OPAL_UPDATE_MANIFEST.json"))

    test_case.assertTrue(version, "OPAL_VERSION.txt لا يحتوي رقم إصدار.")
    test_case.assertRegex(release_name, rf"OPAL Update {re.escape(version)} R\d+ - .+")
    test_case.assertEqual(manifest["version"], version)
    test_case.assertEqual(manifest["version_name"], release_name)
    test_case.assertGreaterEqual(manifest["package_revision"], min_revision)
    # Releases before R114 were code-only.  R114 is the first dashboard
    # release in this line that legitimately changes the School schema, so
    # the manifest must explicitly describe whether migrations are required.
    test_case.assertIn(manifest.get("code_only"), (True, False))
    if manifest.get("code_only") is False:
        test_case.assertTrue(manifest.get("database_changes"))
        test_case.assertTrue(manifest.get("model_changes"))
        test_case.assertTrue(manifest.get("migration_changes"))
