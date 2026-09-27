#!/usr/bin/env python3
"""Read-only R125 CSS authority gate for OPAL ERP.

This check uses only the Python standard library and is intentionally independent
from Django. It verifies the single local stylesheet contract before deployment.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def source_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(part in {".git", "media", "staticfiles", "__pycache__"} for part in path.parts):
            continue
        if path.name.startswith("test_") or "/tests/" in rel or "/migrations/" in rel or rel.startswith("tools/"):
            continue
        if path.suffix.lower() in {".py", ".html", ".js"}:
            yield path


def verify(root: Path) -> dict:
    issues: list[str] = []
    css_path = root / "static/css/opal_theme_system.css"
    css_files = sorted(p.relative_to(root).as_posix() for p in root.rglob("*.css") if ".git" not in p.parts)
    if css_files != ["static/css/opal_theme_system.css"]:
        issues.append(f"local CSS files are not exactly one authority: {css_files}")
    if (root / "static/learning_platform/css/platform.css").exists():
        issues.append("parallel learning_platform/css/platform.css still exists")
    if not css_path.exists():
        issues.append("central CSS authority is missing")
        return {"ok": False, "issues": issues}

    css = css_path.read_text(encoding="utf-8")
    source = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in source_files(root))

    html_violations = []
    for path in root.rglob("*.html"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"<style\b", text, re.I):
            html_violations.append(f"style tag: {path.relative_to(root)}")
        if "block extra_css" in text or "block extra_head" in text:
            html_violations.append(f"CSS escape block: {path.relative_to(root)}")
        for link in re.findall(r"<link[^>]+stylesheet[^>]*>", text, re.I):
            if "cdn.jsdelivr.net" in link or "unpkg.com/leaflet" in link:
                continue
            if "css/opal_theme_system.css" not in link:
                html_violations.append(f"non-authority stylesheet: {path.relative_to(root)}")
    issues.extend(html_violations)

    if re.search(r"opal-(?:dark|green|light)-mode", source):
        issues.append("legacy theme-mode classes remain in runtime source")
    if "BEGIN LEGACY SOURCE" in css or "END LEGACY SOURCE" in css:
        issues.append("legacy CSS source markers remain")

    defs = set(re.findall(r"(--opal-[\w-]+)\s*:", css))
    uses = set(re.findall(r"var\(\s*(--opal-[\w-]+)", css)) | set(re.findall(r"(--opal-[\w-]+)", source))
    unused_vars = sorted(defs - uses)
    if unused_vars:
        issues.append(f"unused OPAL variables: {unused_vars}")

    tokens = set(re.findall(r"(?<![\w-])([A-Za-z_][\w-]*)(?![\w-])", source))
    classes = set(re.findall(r"\.([A-Za-z_][\w-]*)", css))
    dynamic_prefixes = (
        "is-", "status-", "bg-", "border-", "col-", "bi-", "type-", "sibling-", "receipt-copy",
        "alert-", "btn-", "text-", "d-", "m-", "mt-", "mb-", "ms-", "me-", "mx-", "my-", "p-",
        "pt-", "pb-", "ps-", "pe-", "px-", "py-", "w-", "h-", "flex-", "justify-", "align-",
        "gap-", "position-", "top-", "bottom-", "start-", "end-", "translate-", "rounded-", "shadow-",
        "overflow-", "object-", "fs-", "fw-", "lh-", "order-", "z-", "float-", "ratio-", "visible-",
        "invisible-", "list-", "nav-", "page-", "table-", "form-", "input-", "accordion-", "modal-",
        "dropdown-", "offcanvas-", "toast-", "tooltip-", "popover-", "pagination-", "row-", "container-",
        "apexcharts-", "chartjs-"
    )
    framework = {
        "accordion-body", "accordion-button", "accordion-item", "bg-white", "btn-group", "dropdown-item",
        "invalid-feedback", "valid-feedback", "errorlist", "was-validated", "modal-backdrop", "modal-footer",
        "offcanvas-header", "page-item", "page-link", "toast-container", "toast-header", "tooltip-inner",
        "popover", "pagination", "btn", "card", "table", "badge", "alert", "nav", "container", "row",
        "col", "small", "lead", "mark", "ratio", "form-control", "form-select", "modal-content",
        "offcanvas", "toast"
    }
    unused_classes = sorted(
        c for c in classes
        if c not in tokens and c not in framework and not any(c.startswith(p) for p in dynamic_prefixes)
    )
    if unused_classes:
        issues.append(f"unused CSS class selectors: {unused_classes}")

    for path in root.rglob("*.html"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "new Chart(" not in text:
            continue
        if re.search(r"(?:borderColor|backgroundColor|ticks\s*:\s*\{[^}]*color|grid\s*:\s*\{[^}]*color)\s*:\s*[\"'](?:#|rgb|hsl)", text):
            issues.append(f"hardcoded chart color in {path.relative_to(root)}")

    report = {
        "ok": not issues,
        "issues": issues,
        "css_files": css_files,
        "css_bytes": css_path.stat().st_size,
        "opal_variables": len(defs),
        "css_classes": len(classes),
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = verify(Path(args.root).resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("PASS" if report["ok"] else "FAIL", "OPAL R125 CSS Authority")
        for issue in report["issues"]:
            print("ERROR:", issue)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
