from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Profile, Role


def get_profile(user) -> Profile:
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            "role": Role.ADMIN if user.is_superuser else Role.STUDENT,
            "full_name": user.get_full_name() or user.username,
            "is_email_verified": user.is_superuser,
            "must_change_password": not user.is_superuser,
        },
    )
    return profile


def role_home_url_name(user) -> str:
    profile = get_profile(user)
    if profile.is_admin:
        return "portal:admin_dashboard"
    if profile.is_teacher:
        return "portal:teacher_dashboard"
    return "portal:student_dashboard"


def _password_gate(request, profile):
    if profile.must_change_password:
        return redirect("accounts:force_password_change")
    return None


def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = get_profile(request.user)
        request.profile = profile
        blocked = _password_gate(request, profile)
        if blocked:
            return blocked
        if profile.is_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Faqat administrator kira oladi.")
        return redirect(role_home_url_name(request.user))

    return _wrapped


def student_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = get_profile(request.user)
        request.profile = profile
        blocked = _password_gate(request, profile)
        if blocked:
            return blocked
        if profile.is_admin:
            messages.error(request, "Admin student paneliga kira olmaydi.")
            return redirect("portal:admin_dashboard")
        if profile.is_teacher:
            messages.error(request, "Teacher student paneliga kira olmaydi.")
            return redirect("portal:teacher_dashboard")
        if profile.is_student:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Faqat student kira oladi.")
        return redirect("accounts:login")

    return _wrapped


def teacher_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = get_profile(request.user)
        request.profile = profile
        blocked = _password_gate(request, profile)
        if blocked:
            return blocked
        if profile.is_admin:
            messages.error(request, "Admin teacher paneliga kira olmaydi.")
            return redirect("portal:admin_dashboard")
        if profile.is_teacher:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Faqat teacher kira oladi.")
        return redirect(role_home_url_name(request.user))

    return _wrapped


def superuser_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = get_profile(request.user)
        request.profile = profile
        blocked = _password_gate(request, profile)
        if blocked:
            return blocked
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Faqat Super Admin buni qila oladi.")
        return redirect("portal:admin_dashboard")

    return _wrapped
