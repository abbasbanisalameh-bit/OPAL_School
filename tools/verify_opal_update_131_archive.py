#!/usr/bin/env python3
"""Verify that an OPAL Update 131.7 ZIP is complete and contains code only."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import PurePosixPath, Path

EXPECTED_VERSION = "131.7"
MIN_PACKAGE_REVISION = 35
REQUIRED = {
    "manage.py",
    "requirements.txt",
    "OPAL_VERSION.txt",
    "OPAL_RELEASE_NAME.txt",
    "OPAL_UPDATE_MANIFEST.json",
    "core/update_engine_runtime.py",
    "tools/validate_opal_update_131_source.py",
    "tools/verify_opal_update_131_archive.py",
    "tools/verify_opal_css_authority_r125.py",
    "core/test_update131_7_r125_css_sovereignty_contract.py",
    "OPAL_CSS_AUTHORITY_CONTRACT_AR.md",
    "INSTALL_OPAL_UPDATE_131_7_R125_CSS_SOVEREIGNTY_AR.md",
    "OPAL_UPDATE_131_7_R125_RELEASE_NOTES_AR.md",
    "static/css/opal_theme_system.css",
    "static/js/opal_erp.js",
    "templates/base/base.html",
    "templates/learning_platform/base.html",
    "templates/learning_platform/service-worker.js",
    "static/learning_platform/js/platform.js",
    "core/templatetags/opal_subjects.py",
    "core/subject_ui_contracts.py",
    "documents/templates/documents/student_certificate.html",
    "transport/templates/transport/tracking/manager.html",
    "transport/templates/transport/parent/dashboard.html",
    "transport/templates/transport/driver/dashboard.html",
    "transport/templates/transport/trips/detail.html",
    "transport/templates/transport/family_locations/form.html",
}
FORBIDDEN_PARTS = {
    ".git", ".venv", "venv", "env", "media", "uploads", "staticfiles",
    "collected_static", "__pycache__", ".pytest_cache", "backups", "backup",
}
FORBIDDEN_NAMES = {"db.sqlite3", ".env", ".coverage"}
FORBIDDEN_SUFFIXES = {
    ".sqlite", ".sqlite3", ".db", ".pyc", ".pyo", ".pyd", ".zip", ".tar",
    ".tgz", ".bak", ".backup", ".log",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(path: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.is_file() or not zipfile.is_zipfile(path):
        return {"ok": False, "archive": str(path), "errors": ["الملف ليس ZIP صالحًا."], "warnings": []}

    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            errors.append(f"عضو تالف داخل الحزمة: {bad}")
        raw_names = [item.filename.replace("\\", "/") for item in archive.infolist()]
        file_names = {name.rstrip("/") for name in raw_names if name and not name.endswith("/")}

        manage_candidates = [name for name in file_names if name == "manage.py" or name.endswith("/manage.py")]
        if len(manage_candidates) != 1:
            errors.append("يجب أن تحتوي الحزمة على مشروع واحد وملف manage.py واحد.")
            prefix = ""
        else:
            manage = PurePosixPath(manage_candidates[0])
            prefix = "" if str(manage.parent) == "." else f"{manage.parent.as_posix()}/"

        normalized = set()
        for info in archive.infolist():
            name = info.filename.replace("\\", "/")
            pure = PurePosixPath(name)
            if not name or pure.is_absolute() or ".." in pure.parts:
                errors.append(f"مسار غير آمن: {name!r}")
                continue
            unix_mode = (info.external_attr >> 16) & 0o170000
            if unix_mode == 0o120000:
                errors.append(f"رابط رمزي محظور: {name}")
            relative = name[len(prefix):] if prefix and name.startswith(prefix) else name
            relative = relative.rstrip("/")
            if not relative:
                continue
            normalized.add(relative)
            parts = PurePosixPath(relative).parts
            lowered_parts = {part.lower() for part in parts}
            basename = parts[-1]
            suffix = PurePosixPath(basename).suffix.lower()
            if lowered_parts & {part.lower() for part in FORBIDDEN_PARTS}:
                errors.append(f"مجلد تشغيل/خاص محظور: {relative}")
            if basename in FORBIDDEN_NAMES or (basename.startswith(".env") and basename != ".env.example"):
                errors.append(f"ملف سري أو قاعدة بيانات محظور: {relative}")
            if suffix in FORBIDDEN_SUFFIXES:
                errors.append(f"امتداد محظور داخل الحزمة: {relative}")

        missing = sorted(REQUIRED - normalized)
        if missing:
            errors.append("ملفات مطلوبة مفقودة: " + ", ".join(missing))

        def read_text(relative: str) -> str:
            member = f"{prefix}{relative}" if prefix else relative
            try:
                return archive.read(member).decode("utf-8").strip()
            except (KeyError, UnicodeDecodeError):
                return ""

        if read_text("OPAL_VERSION.txt") != EXPECTED_VERSION:
            errors.append("هوية OPAL_VERSION.txt داخل الحزمة ليست 131.7.")
        release_name = read_text("OPAL_RELEASE_NAME.txt")
        if not re.fullmatch(r"OPAL Update 131\.7 R\d+ - .+", release_name):
            errors.append("اسم الإصدار داخل الحزمة لا يطابق هوية Update 131.7.")
        manifest_text = read_text("OPAL_UPDATE_MANIFEST.json")
        try:
            manifest = json.loads(manifest_text)
        except json.JSONDecodeError:
            manifest = {}
            errors.append("OPAL_UPDATE_MANIFEST.json غير صالح.")
        if manifest.get("version") != EXPECTED_VERSION or manifest.get("version_name") != release_name:
            errors.append("بيانات manifest لا تطابق إصدار Update 131.7.")
        if not manifest.get("code_only"):
            errors.append("manifest لا يثبت أن الحزمة code-only.")
        revision = manifest.get("package_revision")
        if not isinstance(revision, int) or revision < MIN_PACKAGE_REVISION:
            errors.append("مراجعة الحزمة الحالية يجب أن تكون 32 أو أحدث لتحديث 131.7.")

    unique_errors = list(dict.fromkeys(errors))
    return {
        "ok": not unique_errors,
        "archive": str(path),
        "sha256": sha256(path),
        "files": len(file_names),
        "errors": unique_errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = verify(Path(args.archive).resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("PASS" if report["ok"] else "FAIL", "OPAL Update 131 archive")
        print(f"- files: {report.get('files', 0)}")
        print(f"- sha256: {report.get('sha256', '')}")
        for warning in report["warnings"]:
            print(f"WARNING: {warning}")
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
