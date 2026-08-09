from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.forms import AdminSetPasswordForm, AdminUserCreateForm, AdminUserUpdateForm
from accounts.models import Profile, Role
from accounts.permissions import admin_required, get_profile
from accounts.services import create_user_by_admin, set_temporary_password, sync_role_side_effects

User = get_user_model()


@admin_required
def admin_users(request):
    q = (request.GET.get("q") or "").strip()
    role = (request.GET.get("role") or "").strip()
    profiles = Profile.objects.select_related("user").all()
    if q:
        profiles = profiles.filter(
            Q(full_name__icontains=q)
            | Q(user__username__icontains=q)
            | Q(user__email__icontains=q)
            | Q(phone__icontains=q)
        )
    if role in {Role.ADMIN, Role.TEACHER, Role.STUDENT}:
        profiles = profiles.filter(role=role)

    create_form = AdminUserCreateForm(actor=request.user)
    return render(
        request,
        "portal/admin/users.html",
        {
            "profiles": profiles,
            "create_form": create_form,
            "q": q,
            "role": role,
            "is_super_admin": request.user.is_superuser,
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_user_create(request):
    form = AdminUserCreateForm(request.POST or None, actor=request.user)
    if request.method == "POST" and form.is_valid():
        user = create_user_by_admin(
            full_name=form.cleaned_data["full_name"],
            username=form.cleaned_data["username"],
            email=form.cleaned_data.get("email") or "",
            password=form.cleaned_data["temporary_password"],
            role=form.cleaned_data["role"],
            phone=form.cleaned_data.get("phone") or "",
            is_active=form.cleaned_data.get("is_active", True),
        )
        messages.success(
            request,
            f"Foydalanuvchi yaratildi: {user.username} ({user.profile.get_role_display()}). "
            "Birinchi kirishda parol almashtiriladi.",
        )
        return redirect("portal:admin_users")
    return render(
        request,
        "portal/admin/user_create.html",
        {"form": form, "is_super_admin": request.user.is_superuser},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_user_edit(request, user_id):
    target = get_object_or_404(User.objects.select_related("profile"), pk=user_id)
    profile = target.profile

    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, "Super Adminni tahrirlash mumkin emas.")
        return redirect("portal:admin_users")
    if profile.is_admin and not request.user.is_superuser and target.pk != request.user.pk:
        messages.error(request, "Admin foydalanuvchini faqat Super Admin tahrirlay oladi.")
        return redirect("portal:admin_users")

    initial = {
        "full_name": profile.full_name,
        "username": target.username,
        "email": target.email,
        "phone": profile.phone,
        "role": profile.role,
        "is_active": target.is_active,
    }
    form = AdminUserUpdateForm(
        request.POST or None,
        actor=request.user,
        target_user=target,
        initial=initial,
    )

    if request.method == "POST" and form.is_valid():
        target.username = form.cleaned_data["username"]
        target.email = form.cleaned_data.get("email") or ""
        target.is_active = form.cleaned_data.get("is_active", False)
        target.save()
        profile.full_name = form.cleaned_data["full_name"]
        profile.phone = form.cleaned_data.get("phone") or ""
        profile.save(update_fields=["full_name", "phone", "updated_at"])
        sync_role_side_effects(target, form.cleaned_data["role"])
        messages.success(request, "Foydalanuvchi yangilandi.")
        return redirect("portal:admin_users")

    return render(
        request,
        "portal/admin/user_edit.html",
        {
            "form": form,
            "target": target,
            "profile": profile,
            "is_super_admin": request.user.is_superuser,
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_user_password(request, user_id):
    target = get_object_or_404(User.objects.select_related("profile"), pk=user_id)
    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, "Super Admin parolini o‘zgartira olmaysiz.")
        return redirect("portal:admin_users")
    if target.profile.is_admin and not request.user.is_superuser and target.pk != request.user.pk:
        messages.error(request, "Admin parolini faqat Super Admin o‘zgartira oladi.")
        return redirect("portal:admin_users")

    form = AdminSetPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        set_temporary_password(target, form.cleaned_data["temporary_password"])
        messages.success(
            request,
            f"{target.username} uchun yangi vaqtinchalik parol berildi. "
            "Keyingi kirishda parol almashtiriladi.",
        )
        return redirect("portal:admin_users")

    return render(
        request,
        "portal/admin/user_password.html",
        {"form": form, "target": target},
    )


@admin_required
@require_http_methods(["POST"])
def admin_user_toggle(request, user_id):
    target = get_object_or_404(User.objects.select_related("profile"), pk=user_id)
    if target.pk == request.user.pk:
        messages.error(request, "O‘zingizni deaktiv qila olmaysiz.")
        return redirect("portal:admin_users")
    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, "Super Adminni o‘zgartira olmaysiz.")
        return redirect("portal:admin_users")
    if target.profile.is_admin and not request.user.is_superuser:
        messages.error(request, "Admin holatini faqat Super Admin o‘zgartira oladi.")
        return redirect("portal:admin_users")

    target.is_active = not target.is_active
    target.save(update_fields=["is_active"])
    state = "aktivlashtirildi" if target.is_active else "deaktiv qilindi"
    messages.success(request, f"{target.username} {state}.")
    return redirect("portal:admin_users")
