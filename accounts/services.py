import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from .models import (
    EmailVerificationToken,
    PasswordResetToken,
    Role,
    StudentProfile,
)

User = get_user_model()

EMAIL_TOKEN_HOURS = 24
PASSWORD_RESET_HOURS = 1


def sync_role_side_effects(user, role: str) -> None:
    profile = user.profile
    profile.role = role
    profile.save(update_fields=["role", "updated_at"])

    if role == Role.STUDENT:
        StudentProfile.objects.get_or_create(user=user)
        user.is_staff = False
        user.is_superuser = False
        user.save(update_fields=["is_staff", "is_superuser"])
    elif role == Role.TEACHER:
        user.is_staff = False
        user.is_superuser = False
        user.save(update_fields=["is_staff", "is_superuser"])
    elif role == Role.ADMIN:
        user.is_staff = True
        user.save(update_fields=["is_staff"])


@transaction.atomic
def create_user_by_admin(
    *,
    full_name: str,
    username: str,
    email: str,
    password: str,
    role: str,
    phone: str = "",
    is_active: bool = True,
) -> User:
    user = User.objects.create_user(
        username=username.strip(),
        email=(email or "").strip(),
        password=password,
        is_active=is_active,
    )
    profile = user.profile
    profile.full_name = full_name.strip()
    profile.phone = phone.strip()
    profile.must_change_password = True
    profile.is_email_verified = True
    profile.save()
    sync_role_side_effects(user, role)
    return user


@transaction.atomic
def set_temporary_password(user, password: str) -> None:
    user.set_password(password)
    user.save(update_fields=["password"])
    profile = user.profile
    profile.must_change_password = True
    profile.save(update_fields=["must_change_password", "updated_at"])


@transaction.atomic
def register_student(
    *,
    full_name: str,
    email: str,
    phone: str,
    password: str,
) -> User:
    email_clean = email.strip().lower()
    user = User.objects.create_user(
        username=email_clean,
        email=email_clean,
        password=password,
        is_active=True,
    )
    profile = user.profile
    profile.full_name = full_name.strip()
    profile.phone = phone.strip()
    profile.role = Role.STUDENT
    profile.must_change_password = False
    profile.is_email_verified = False
    profile.save()
    StudentProfile.objects.get_or_create(user=user)
    return user


def _new_token() -> str:
    return secrets.token_urlsafe(32)


def create_email_verification_token(user) -> EmailVerificationToken:
    EmailVerificationToken.objects.filter(user=user, is_used=False).update(is_used=True)
    return EmailVerificationToken.objects.create(user=user, token=_new_token())


def _token_expired(created_at, hours: int) -> bool:
    return timezone.now() > created_at + timedelta(hours=hours)


@transaction.atomic
def verify_email_token(token: str) -> User | None:
    row = (
        EmailVerificationToken.objects.select_related("user", "user__profile")
        .filter(token=token, is_used=False)
        .first()
    )
    if not row:
        return None
    if _token_expired(row.created_at, EMAIL_TOKEN_HOURS):
        return None
    row.is_used = True
    row.save(update_fields=["is_used"])
    profile = row.user.profile
    profile.is_email_verified = True
    profile.save(update_fields=["is_email_verified", "updated_at"])
    return row.user


def create_password_reset_token(user) -> PasswordResetToken:
    PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
    return PasswordResetToken.objects.create(user=user, token=_new_token())


def get_valid_password_reset_token(token: str) -> PasswordResetToken | None:
    row = (
        PasswordResetToken.objects.select_related("user")
        .filter(token=token, is_used=False)
        .first()
    )
    if not row:
        return None
    if _token_expired(row.created_at, PASSWORD_RESET_HOURS):
        return None
    return row


@transaction.atomic
def reset_password_with_token(token: str, password: str) -> User | None:
    row = get_valid_password_reset_token(token)
    if not row:
        return None
    user = row.user
    user.set_password(password)
    user.save(update_fields=["password"])
    row.is_used = True
    row.save(update_fields=["is_used"])
    profile = user.profile
    profile.must_change_password = False
    profile.save(update_fields=["must_change_password", "updated_at"])
    return user


def _absolute_url(request, path: str) -> str:
    return request.build_absolute_uri(path)


def send_verification_email(request, user) -> EmailVerificationToken:
    token_row = create_email_verification_token(user)
    path = reverse("accounts:verify_email_confirm", kwargs={"token": token_row.token})
    link = _absolute_url(request, path)
    send_mail(
        subject="Email manzilingizni tasdiqlang — FOR CENTRE",
        message=(
            f"Assalomu alaykum, {user.profile.display_name}!\n\n"
            f"Emailni tasdiqlash uchun quyidagi havolani oching:\n{link}\n\n"
            f"Havola {EMAIL_TOKEN_HOURS} soat amal qiladi.\n"
            f"Agar bu so‘rovni siz yubormagan bo‘lsangiz, e’tiborsiz qoldiring."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return token_row


def send_password_reset_email(request, user) -> PasswordResetToken:
    token_row = create_password_reset_token(user)
    path = reverse("accounts:password_reset_confirm", kwargs={"token": token_row.token})
    link = _absolute_url(request, path)
    send_mail(
        subject="Parolni tiklash — FOR CENTRE",
        message=(
            f"Assalomu alaykum, {user.profile.display_name}!\n\n"
            f"Parolni yangilash uchun quyidagi havolani oching:\n{link}\n\n"
            f"Havola {PASSWORD_RESET_HOURS} soat amal qiladi.\n"
            f"Agar bu so‘rovni siz yubormagan bo‘lsangiz, e’tiborsiz qoldiring."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return token_row
