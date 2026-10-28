"""Source contracts for R160 destructive-demo-reset and audit-log safeguards."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_demo_reset_flag_defaults_to_disabled():
    settings = source("config/settings.py")
    system_data = source("core/system_data.py")
    views = source("core/views.py")
    assert 'OPAL_ENABLE_DEMO_DATA_RESET = env_bool("OPAL_ENABLE_DEMO_DATA_RESET", False)' in settings
    assert "_require_demo_data_reset_enabled()" in system_data
    assert 'if not getattr(settings, "OPAL_ENABLE_DEMO_DATA_RESET", False):' in views


def test_audit_log_is_not_part_of_any_reset_delete_set():
    reset_service = source("core/production_reset.py")
    delete_labels = reset_service.split("DELETE_MODEL_LABELS = (", 1)[1].split("CATEGORY_MODEL_LABELS =", 1)[0]
    assert '"core.AuditLog"' not in delete_labels
    preserved_labels = reset_service.split("PRESERVED_MODEL_LABELS = (", 1)[1].split("PRESERVED_LABELS_AR =", 1)[0]
    assert '"core.AuditLog"' in preserved_labels
    demo_reset = source("core/system_data.py")
    reset_block = demo_reset.split("def reset_all_operational_data", 1)[1].split("def _guardian_index", 1)[0]
    assert "_delete_all(AuditLog)" not in reset_block


def test_demo_records_are_marked_and_custom_sizes_fail_before_reset():
    system_data = source("core/system_data.py")
    assert system_data.count("is_demo=True") >= 2
    function = system_data.split("def seed_system_data", 1)[1].split("from accounts.models", 1)[0]
    assert "if supplied_counts != expected_counts:" in function
    assert "_require_demo_data_reset_enabled()" in function
    reset_index = system_data.index("reset_all_operational_data(keep_user=user)", system_data.index("def seed_system_data"))
    assert system_data.index("if supplied_counts != expected_counts:") < reset_index


def test_release_identity_advances_from_r159_without_schema_changes():
    manifest = json.loads(source("OPAL_UPDATE_MANIFEST.json"))
    release_name = source("OPAL_RELEASE_NAME.txt").strip()
    assert manifest["package_revision"] == 160
    assert manifest["baseline"].endswith("R159 - Unified Timetable Workspace")
    assert manifest["version"] == source("OPAL_VERSION.txt").strip() == "131.7"
    assert manifest["version_name"] == release_name
    assert manifest["code_only"] is True
