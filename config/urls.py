from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path, re_path
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.static import serve
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required
from core import views as core_views
from config.url_groups import CORE_URLPATTERNS, PRIMARY_URLPATTERNS, SCHOOL_URLPATTERNS


admin.site.site_header = "إدارة نظام أوبال"
admin.site.site_title = "أوبال"
admin.site.index_title = "إدارة البيانات الرئيسية"

handler400 = "core.security.bad_request"
handler403 = "core.security.permission_denied"
handler404 = "core.security.page_not_found"
handler500 = "core.security.server_error"


opal_login_view = never_cache(
    ensure_csrf_cookie(
        LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True,
        )
    )
)


urlpatterns = [
    path("transport/", include("transport.urls")),
    *PRIMARY_URLPATTERNS,
    path(
        'accounts/login/',
        opal_login_view,
        name='login',
    ),
    path('login/', RedirectView.as_view(pattern_name='login', permanent=False)),
    *CORE_URLPATTERNS[:1],
    path('admin/', core_views.admin_disabled, name='admin_disabled'),
    *CORE_URLPATTERNS[1:],
    *SCHOOL_URLPATTERNS,
]

if settings.OPAL_ENABLE_OPENEMIS:
    urlpatterns.append(path('openemis/', include('openemis_integration.urls')))

if settings.OPAL_ENABLE_DEVELOPMENT_CENTER:
    urlpatterns.append(path('development/', include('development_center.urls')))

# OPAL production media delivery
#
# django.conf.urls.static.static() intentionally returns no route when
# DEBUG=False, so it cannot be used as the production media bridge here.
# OPAL serves uploaded media through Django itself and keeps the endpoint
# authenticated so school/student/teacher/driver images are not public.
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        login_required(serve),
        {"document_root": settings.MEDIA_ROOT},
    ),
]
