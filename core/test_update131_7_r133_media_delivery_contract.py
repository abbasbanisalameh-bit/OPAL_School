from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URLS = (ROOT / "config" / "urls.py").read_text(encoding="utf-8")


def test_media_route_is_not_debug_gated():
    marker = 'urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)'
    assert marker in URLS
    assert 'if settings.DEBUG:\n    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)' not in URLS
