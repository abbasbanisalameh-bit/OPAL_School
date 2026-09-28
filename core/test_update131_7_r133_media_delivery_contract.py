from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URLS = (ROOT / "config" / "urls.py").read_text(encoding="utf-8")


def test_media_route_is_not_debug_gated():
    assert 're_path(\n        r"^media/(?P<path>.*)$",\n        login_required(serve),' in URLS
    assert 'urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)' not in URLS


def test_media_route_requires_login():
    assert 'login_required(serve)' in URLS
    assert '"document_root": settings.MEDIA_ROOT' in URLS
