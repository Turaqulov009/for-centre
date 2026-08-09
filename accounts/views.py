from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from accounts.permissions import get_profile, role_home_url_name

from .forms import (
    ForcePasswordChangeForm,
    ForgotPasswordForm,
    LoginForm,
    PasswordResetConfirmForm,
    RegisterForm,
)
from . import services

User = get_user_model()


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        profile = get_profile(request.user)
        if profile.must_change_password:
            return redirect("accounts:force_password_change")
        if profile.is_student and not profile.is_email_verified:
            return redirect("accounts:verify_email_gate")
        return redirect(role_home_url_name(request.user))

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        profile = get_profile(user)
        if profile.must_change_password:
            messages.info(request, "Davom etish uchun yangi parol o‘rnating.")
            return redirect("accounts:force_password_change")
        if profile.is_student and not profile.is_email_verified:
            messages.info(request, "Davom etish uchun emailni tasdiqlang.")
            return redirect("accounts:verify_email_gate")
        messages.success(request, "Xush kelibsiz!")
        return redirect(role_home_url_name(user))

    return render(request, "accounts/login.html", {"form": form})


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect("accounts:login")


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect(role_home_url_name(request.user))

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = services.register_student(
            full_name=form.cleaned_data["full_name"],
            email=form.cleaned_data["email"],
            phone=form.cleaned_data["phone"],
            password=form.cleaned_data["password1"],
        )
        services.send_verification_email(request, user)
        messages.success(
            request,
            "Ro‘yxatdan o‘tdingiz. Emailingizga tasdiqlash havolasi yuborildi. "
            "Kirib, emailni tasdiqlang.",
        )
        return redirect("accounts:login")

    return render(request, "accounts/register.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def verify_email_gate(request):
    profile = get_profile(request.user)
    if profile.is_email_verified:
        return redirect(role_home_url_name(request.user))

    if request.method == "POST":
        if not request.user.email:
            messages.error(request, "Email manzil topilmadi.")
        else:
            services.send_verification_email(request, request.user)
            messages.success(request, "Tasdiqlash havolasi qayta yuborildi.")
        return redirect("accounts:verify_email_gate")

    return render(
        request,
        "accounts/verify_email.html",
        {"email": request.user.email},
    )


@require_http_methods(["GET"])
def verify_email_confirm(request, token):
    user = services.verify_email_token(token)
    if not user:
        messages.error(request, "Tasdiqlash havolasi noto‘g‘ri yoki muddati o‘tgan.")
        if request.user.is_authenticated:
            return redirect("accounts:verify_email_gate")
        return redirect("accounts:login")

    messages.success(request, "Email muvaffaqiyatli tasdiqlandi.")
    if request.user.is_authenticated and request.user.pk == user.pk:
        return redirect(role_home_url_name(user))
    return redirect("accounts:login")


@require_http_methods(["GET", "POST"])
def forgot_password(request):
    if request.user.is_authenticated:
        return redirect(role_home_url_name(request.user))

    form = ForgotPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if user and user.email:
            services.send_password_reset_email(request, user)
        messages.success(
            request,
            "Agar bu email tizimda bo‘lsa, parolni tiklash havolasi yuborildi.",
        )
        return redirect("accounts:login")

    return render(request, "accounts/forgot_password.html", {"form": form})


@require_http_methods(["GET", "POST"])
def password_reset_confirm(request, token):
    token_row = services.get_valid_password_reset_token(token)
    if not token_row:
        messages.error(request, "Parolni tiklash havolasi noto‘g‘ri yoki muddati o‘tgan.")
        return redirect("accounts:forgot_password")

    form = PasswordResetConfirmForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = services.reset_password_with_token(token, form.cleaned_data["password1"])
        if not user:
            messages.error(request, "Parolni tiklash havolasi noto‘g‘ri yoki muddati o‘tgan.")
            return redirect("accounts:forgot_password")
        messages.success(request, "Parol yangilandi. Endi tizimga kiring.")
        return redirect("accounts:login")

    return render(
        request,
        "accounts/password_reset_confirm.html",
        {"form": form},
    )


@login_required
@require_http_methods(["GET", "POST"])
def force_password_change(request):
    profile = get_profile(request.user)
    if not profile.must_change_password:
        return redirect(role_home_url_name(request.user))

    form = ForcePasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        update_session_auth_hash(request, request.user)
        profile = get_profile(request.user)
        if profile.is_student and not profile.is_email_verified:
            messages.success(request, "Parol yangilandi. Endi emailni tasdiqlang.")
            return redirect("accounts:verify_email_gate")
        messages.success(request, "Parol yangilandi. Endi dashboard ochildi.")
        return redirect(role_home_url_name(request.user))

    return render(
        request,
        "accounts/force_password_change.html",
        {"form": form},
    )
