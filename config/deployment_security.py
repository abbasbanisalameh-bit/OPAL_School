"""Deployment security settings for OPAL.

Production secrets are loaded from OPAL_SECRET_KEY when supplied. If it is
omitted, a strong key is generated once in private storage outside the source
tree; it is never regenerated on subsequent starts. Reverse-proxy IP headers
are handled separately by core.client_ip and are not trusted by default.
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path

from .environment import env_bool


def get_secret_key(*, debug: bool, base_dir: Path) -> str:
    """Resolve a stable secret key without an insecure production fallback."""
    configured = os.environ.get("OPAL_SECRET_KEY", "").strip()
    if configured:
        if len(configured) < 50:
            raise RuntimeError(
                "OPAL_SECRET_KEY must contain at least 50 characters. "
                "Use a randomly generated production secret."
            )
        if configured.startswith("django-insecure-"):
            raise RuntimeError("OPAL_SECRET_KEY must not use Django's insecure placeholder.")
        return configured

    if debug:
        # Development-only value; production never falls back to this constant.
        return "django-insecure-local-development-only-key"

    configured_path = os.environ.get("OPAL_SECRET_KEY_FILE", "").strip()
    configured_storage = (
        os.environ.get("OPAL_SYSTEM_STORAGE_DIR", "").strip()
        or os.environ.get("OPAL_PRIVATE_BACKUP_DIR", "").strip()
    )
    if configured_path:
        key_path = Path(configured_path).expanduser()
    else:
        storage_root = (
            Path(configured_storage).expanduser()
            if configured_storage
            else Path(base_dir).resolve().parent / "opal_private_backups"
        )
        key_path = storage_root / "security" / "django_secret_key"
    key_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        descriptor = os.open(str(key_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        key = secrets.token_urlsafe(64)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(key)
            stream.flush()
            os.fsync(stream.fileno())

    try:
        os.chmod(key_path, 0o600)
        key = key_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise RuntimeError(
            "Unable to read the persistent OPAL secret key. Set OPAL_SECRET_KEY "
            "or OPAL_SECRET_KEY_FILE to a secure persistent location."
        ) from exc

    if len(key) < 50 or key.startswith("django-insecure-"):
        raise RuntimeError(
            "The persisted OPAL secret key is invalid. Preserve the existing file "
            "and configure a strong OPAL_SECRET_KEY before restarting."
        )
    return key


def build_proxy_ssl_header() -> tuple[str, str]:
    return ("HTTP_X_FORWARDED_PROTO", "https")


def build_production_security(*, debug: bool) -> dict[str, object]:
    if debug:
        return {}

    hsts_seconds = int(os.environ.get("OPAL_HSTS_SECONDS", "0"))
    include_subdomains = env_bool("OPAL_HSTS_INCLUDE_SUBDOMAINS", False) and hsts_seconds > 0
    preload = env_bool("OPAL_HSTS_PRELOAD", False) and hsts_seconds > 0
    return {
        "SECURE_CONTENT_TYPE_NOSNIFF": True,
        "SESSION_COOKIE_SECURE": True,
        "CSRF_COOKIE_SECURE": True,
        "X_FRAME_OPTIONS": "DENY",
        "SECURE_REFERRER_POLICY": "same-origin",
        "SECURE_SSL_REDIRECT": env_bool("OPAL_SECURE_SSL_REDIRECT", True),
        "SECURE_HSTS_SECONDS": hsts_seconds,
        "SECURE_HSTS_INCLUDE_SUBDOMAINS": include_subdomains,
        "SECURE_HSTS_PRELOAD": preload,
    }
