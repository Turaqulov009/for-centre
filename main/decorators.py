from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Profile


def get_profile(user):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            "role": Profile.Role.ADMIN if user.is_superuser else Profile.Role.STUDENT,
            "full_name": user.get_full_name() or user.username,
        },
    )
    return profile


def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = get_profile(request.user)
        request.profile = profile
        if profile.is_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Faqat admin kira oladi.")
        return redirect("portal_home")

    return _wrapped


def teacher_required(view_func):
    """Admin yoki o‘qituvchi."""

    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = get_profile(request.user)
        request.profile = profile
        if profile.is_admin or profile.is_teacher:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Faqat o‘qituvchi yoki admin kira oladi.")
        return redirect("portal_home")

    return _wrapped


def student_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = get_profile(request.user)
        request.profile = profile
        if profile.is_student:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Bu oyna faqat studentlar uchun.")
        return redirect("portal_home")

    return _wrapped
