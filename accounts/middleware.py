from django.shortcuts import redirect
from django.urls import reverse

from accounts.permissions import get_profile


class ForcePasswordChangeMiddleware:
    """Dashboarddan oldin majburiy parol almashtirish va email verification."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path
            allowed_prefixes = (
                reverse("accounts:force_password_change"),
                reverse("accounts:logout"),
                reverse("accounts:login"),
                reverse("accounts:register"),
                reverse("accounts:verify_email_gate"),
                reverse("accounts:forgot_password"),
                "/accounts/verify-email/",
                "/accounts/password/reset/",
                "/static/",
                "/media/",
                "/django-admin/",
            )
            if not any(path.startswith(p) for p in allowed_prefixes):
                profile = get_profile(request.user)
                if profile.must_change_password:
                    return redirect("accounts:force_password_change")
                if profile.is_student and not profile.is_email_verified:
                    return redirect("accounts:verify_email_gate")
        return self.get_response(request)
