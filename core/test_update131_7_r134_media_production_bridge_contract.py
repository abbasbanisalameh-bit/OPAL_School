from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URLS = (ROOT / "config" / "urls.py").read_text(encoding="utf-8")


def test_production_media_bridge_uses_explicit_route():
    assert 'from django.views.static import serve' in URLS
    assert 'from django.contrib.auth.decorators import login_required' in URLS
    assert 'r"^media/(?P<path>.*)$"' in URLS
    assert 'login_required(serve)' in URLS
    assert '"document_root": settings.MEDIA_ROOT' in URLS


def test_old_debug_gated_static_bridge_is_absent():
    assert 'urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)' not in URLS
    assert 'if settings.DEBUG:' not in URLS.split('# OPAL production media delivery', 1)[-1]
