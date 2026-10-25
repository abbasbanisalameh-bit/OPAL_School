import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from core.client_ip import get_client_ip
from config.deployment_security import build_production_security, get_secret_key


class ClientIpResolutionTests(unittest.TestCase):
    def test_ignores_forwarded_header_without_trusted_proxy(self):
        request = SimpleNamespace(META={
            "REMOTE_ADDR": "203.0.113.9",
            "HTTP_X_FORWARDED_FOR": "198.51.100.44",
        })
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_client_ip(request), "203.0.113.9")

    def test_ignores_forwarded_header_when_peer_is_not_trusted(self):
        request = SimpleNamespace(META={
            "REMOTE_ADDR": "203.0.113.9",
            "HTTP_X_FORWARDED_FOR": "198.51.100.44",
        })
        with patch.dict(os.environ, {"OPAL_TRUSTED_PROXY_IPS": "10.0.0.0/8"}, clear=True):
            self.assertEqual(get_client_ip(request), "203.0.113.9")

    def test_walks_trusted_proxy_chain_from_right(self):
        request = SimpleNamespace(META={
            "REMOTE_ADDR": "10.0.0.3",
            "HTTP_X_FORWARDED_FOR": "198.51.100.44, 10.0.0.2",
        })
        with patch.dict(os.environ, {"OPAL_TRUSTED_PROXY_IPS": "10.0.0.0/8"}, clear=True):
            self.assertEqual(get_client_ip(request), "198.51.100.44")

    def test_invalid_forwarded_values_do_not_override_remote(self):
        request = SimpleNamespace(META={
            "REMOTE_ADDR": "10.0.0.3",
            "HTTP_X_FORWARDED_FOR": "attacker-value, 10.0.0.2",
        })
        with patch.dict(os.environ, {"OPAL_TRUSTED_PROXY_IPS": "10.0.0.0/8"}, clear=True):
            self.assertEqual(get_client_ip(request), "10.0.0.3")


class SecretKeyResolutionTests(unittest.TestCase):
    def test_production_key_is_persisted_outside_source_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "project"
            base.mkdir()
            with patch.dict(os.environ, {}, clear=True):
                first = get_secret_key(debug=False, base_dir=base)
                second = get_secret_key(debug=False, base_dir=base)
                self.assertEqual(first, second)
                self.assertGreaterEqual(len(first), 50)
                self.assertFalse(first.startswith("django-insecure-"))
                key_file = base.parent / "opal_private_backups" / "security" / "django_secret_key"
                self.assertTrue(key_file.is_file())
                if os.name == "posix":
                    self.assertEqual(key_file.stat().st_mode & 0o777, 0o600)

    def test_explicit_production_key_is_used(self):
        key = "opal-production-key-" + ("x" * 60)
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"OPAL_SECRET_KEY": key}, clear=True):
            self.assertEqual(get_secret_key(debug=False, base_dir=Path(tmp)), key)


class ProductionSecuritySettingsTests(unittest.TestCase):
    def test_https_redirect_is_enabled_by_default_in_production(self):
        with patch.dict(os.environ, {}, clear=True):
            values = build_production_security(debug=False)
        self.assertTrue(values["SECURE_SSL_REDIRECT"])
        self.assertEqual(values["SECURE_HSTS_SECONDS"], 0)
        self.assertFalse(values["SECURE_HSTS_INCLUDE_SUBDOMAINS"])
        self.assertFalse(values["SECURE_HSTS_PRELOAD"])

    def test_hsts_requires_explicit_seconds_and_subdomain_opt_in(self):
        with patch.dict(os.environ, {
            "OPAL_HSTS_SECONDS": "31536000",
            "OPAL_HSTS_INCLUDE_SUBDOMAINS": "true",
            "OPAL_HSTS_PRELOAD": "false",
        }, clear=True):
            values = build_production_security(debug=False)
        self.assertEqual(values["SECURE_HSTS_SECONDS"], 31536000)
        self.assertTrue(values["SECURE_HSTS_INCLUDE_SUBDOMAINS"])
        self.assertFalse(values["SECURE_HSTS_PRELOAD"])


if __name__ == "__main__":
    unittest.main()
