from pathlib import Path
import re
from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]


class R125CssSovereigntyContractTests(SimpleTestCase):
    def _source_files(self):
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            if any(part in {".git", "media", "staticfiles", "__pycache__"} for part in path.parts):
                continue
            if path.name.startswith("test_") or "/tests/" in rel or "/migrations/" in rel or rel.startswith("tools/"):
                continue
            if path.suffix.lower() in {".py", ".html", ".js"}:
                yield path

    def test_exactly_one_local_css_file_exists(self):
        css_files = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.css"))
        self.assertEqual(css_files, ["static/css/opal_theme_system.css"])

    def test_learning_platform_has_no_parallel_stylesheet(self):
        self.assertFalse((ROOT / "static/learning_platform/css/platform.css").exists())

    def test_no_template_style_blocks_or_css_escape_hatches_exist(self):
        for path in ROOT.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"<style\b", msg=str(path))
            self.assertNotIn("block extra_css", text, msg=str(path))
            self.assertNotIn("block extra_head", text, msg=str(path))

    def test_local_stylesheet_links_point_only_to_authority(self):
        for path in ROOT.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            for link in re.findall(r"<link[^>]+rel=[\"']stylesheet[\"'][^>]*>", text, re.I):
                if "cdn.jsdelivr.net" in link or "unpkg.com/leaflet" in link:
                    continue
                self.assertIn("static/css/opal_theme_system.css", link, msg=f"non-authority CSS in {path}: {link}")

    def test_legacy_theme_mode_classes_are_gone(self):
        for path in self._source_files():
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"opal-(?:dark|green|light)-mode", msg=str(path))

    def test_theme_state_uses_data_attribute(self):
        base = (ROOT / "templates/base/base.html").read_text(encoding="utf-8")
        js = (ROOT / "static/js/opal_erp.js").read_text(encoding="utf-8")
        self.assertIn("data-opal-theme", base)
        self.assertIn('setAttribute("data-opal-theme", resolved)', js)
        self.assertIn("window.OPALTheme.color", js)

    def test_no_inline_style_blocks_control_theme_or_static_visual_values(self):
        for path in ROOT.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r'\bstyle\s*=\s*([\"\'])(.*?)\1', text, re.I | re.S):
                value = match.group(2)
                self.assertNotRegex(value, r"(?i)--opal-|--course-color|(?:^|[;\s])(color|background|background-color|border|box-shadow|fill|stroke|font|filter)\s*:", msg=f"theme/style inline authority in {path}: {value}")

    def test_theme_file_has_no_unused_runtime_class_selectors(self):
        css = (ROOT / "static/css/opal_theme_system.css").read_text(encoding="utf-8")
        source_parts = []
        for path in self._source_files():
            source_parts.append(path.read_text(encoding="utf-8"))
        source = "\n".join(source_parts)
        tokens = set(re.findall(r"(?<![\w-])([A-Za-z_][\w-]*)(?![\w-])", source))
        classes = set(re.findall(r"\.([A-Za-z_][\w-]*)", css))
        dynamic_prefixes = (
            "is-", "status-", "bg-", "border-", "col-", "bi-", "type-", "sibling-",
            "receipt-copy", "alert-", "btn-", "text-", "d-", "m-", "mt-", "mb-", "ms-",
            "me-", "mx-", "my-", "p-", "pt-", "pb-", "ps-", "pe-", "px-", "py-", "w-",
            "h-", "flex-", "justify-", "align-", "gap-", "position-", "top-", "bottom-",
            "start-", "end-", "translate-", "rounded-", "shadow-", "overflow-", "object-",
            "fs-", "fw-", "lh-", "order-", "z-", "float-", "ratio-", "visible-", "invisible-",
            "list-", "nav-", "page-", "table-", "form-", "input-", "accordion-", "modal-",
            "dropdown-", "offcanvas-", "toast-", "tooltip-", "popover-", "pagination-",
            "row-", "container-", "apexcharts-", "chartjs-"
        )
        framework = {
            "accordion-body", "accordion-button", "accordion-item", "bg-white", "btn-group",
            "dropdown-item", "invalid-feedback", "valid-feedback", "errorlist", "was-validated",
            "modal-backdrop", "modal-footer", "offcanvas-header", "page-item", "page-link",
            "toast-container", "toast-header", "tooltip-inner", "popover", "pagination", "btn",
            "card", "table", "badge", "alert", "nav", "container", "row", "col", "small",
            "lead", "mark", "ratio", "form-control", "form-select", "modal-content",
            "offcanvas", "toast"
        }
        unused = sorted(
            name for name in classes
            if name not in tokens
            and name not in framework
            and not any(name.startswith(prefix) for prefix in dynamic_prefixes)
        )
        self.assertEqual(unused, [], msg=f"unused CSS selectors: {unused}")

    def test_theme_file_has_no_unused_opal_custom_properties(self):
        css_path = ROOT / "static/css/opal_theme_system.css"
        css = css_path.read_text(encoding="utf-8")
        source = "\n".join(p.read_text(encoding="utf-8") for p in self._source_files() if p != css_path)
        defs = set(re.findall(r"(--opal-[\w-]+)\s*:", css))
        uses = set(re.findall(r"var\(\s*(--opal-[\w-]+)", css)) | set(re.findall(r"(--opal-[\w-]+)", source))
        self.assertFalse(sorted(defs - uses), msg=f"unused OPAL variables: {sorted(defs - uses)}")

    def test_css_contains_no_legacy_source_markers(self):
        css = (ROOT / "static/css/opal_theme_system.css").read_text(encoding="utf-8")
        self.assertNotIn("BEGIN LEGACY SOURCE", css)
        self.assertNotIn("END LEGACY SOURCE", css)
        self.assertNotIn("R121 cache marker", css)
        self.assertNotIn("R122 cache marker", css)
        self.assertNotIn("R123 cache marker", css)

    def test_chart_templates_consume_css_tokens_instead_of_hardcoded_theme_colors(self):
        for path in ROOT.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            if "new Chart(" not in text:
                continue
            self.assertNotRegex(text, r"(?:borderColor|backgroundColor|ticks\s*:\s*\{[^}]*color|grid\s*:\s*\{[^}]*color)\s*:\s*['\"](?:#|rgb|hsl)", msg=str(path))
