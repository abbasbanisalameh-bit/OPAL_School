from django.apps import apps
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from core.client_ip import get_client_ip


def _ip(request):
    return get_client_ip(request)


def _audit_log_model():
    return apps.get_model("core", "AuditLog")


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    _audit_log_model().objects.create(
        user=user,
        action="login",
        model_name="auth.User",
        object_id=str(user.pk),
        description="تسجيل دخول ناجح",
        ip_address=_ip(request),
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user:
        _audit_log_model().objects.create(
            user=user,
            action="logout",
            model_name="auth.User",
            object_id=str(user.pk),
            description="تسجيل خروج",
            ip_address=_ip(request),
        )
