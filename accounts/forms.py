from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from learning.models import Course

from .models import Role

User = get_user_model()


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        label="To‘liq ism",
        max_length=150,
        widget=forms.TextInput(
            attrs={"placeholder": "Ism Familiya", "autocomplete": "name"}
        ),
    )
    phone = forms.CharField(
        label="Telefon",
        max_length=30,
        widget=forms.TextInput(
            attrs={"placeholder": "+998 XX XXX XX XX", "autocomplete": "tel"}
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"placeholder": "email@example.com", "autocomplete": "email"}
        ),
    )
    password1 = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Parol", "autocomplete": "new-password"}
        ),
    )
    password2 = forms.CharField(
        label="Parolni tasdiqlang",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Parolni qayta kiriting", "autocomplete": "new-password"}
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu email allaqachon ro‘yxatdan o‘tgan.")
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("Bu email bilan akkaunt mavjud.")
        return email

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Parollar mos kelmadi.")
        return cleaned


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"placeholder": "Ro‘yxatdan o‘tgan email", "autocomplete": "email"}
        ),
    )


class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(
        label="Yangi parol",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Yangi parolni tasdiqlang",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Parollar mos kelmadi.")
        return cleaned



class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Login",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username yoki email",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Parol",
                "autocomplete": "current-password",
            }
        ),
    )

    error_messages = {
        "invalid_login": "Login yoki parol noto‘g‘ri.",
        "inactive": "Bu akkaunt deaktiv qilingan.",
    }

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class ForcePasswordChangeForm(SetPasswordForm):
    def save(self, commit=True):
        user = super().save(commit=commit)
        profile = user.profile
        profile.must_change_password = False
        profile.save(update_fields=["must_change_password", "updated_at"])
        return user


class AdminUserCreateForm(forms.Form):
    full_name = forms.CharField(label="To‘liq ism", max_length=150)
    username = forms.CharField(
        label="Login (username)",
        max_length=150,
        help_text="Foydalanuvchi shu login bilan kiradi.",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        help_text="Ixtiyoriy. Berilsa, email orqali ham kirish mumkin.",
    )
    phone = forms.CharField(label="Telefon", max_length=30, required=False)
    temporary_password = forms.CharField(
        label="Vaqtinchalik parol",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        min_length=4,
        help_text="Birinchi kirishda yangi parol o‘rnatish majburiy.",
    )
    role = forms.ChoiceField(label="Role", choices=Role.choices)
    is_active = forms.BooleanField(label="Aktiv", required=False, initial=True)

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        if actor and not actor.is_superuser:
            self.fields["role"].choices = [
                (Role.STUDENT, "Student"),
                (Role.TEACHER, "Teacher"),
            ]

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Bu username band.")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu email band.")
        return email

    def clean_role(self):
        role = self.cleaned_data["role"]
        if role == Role.ADMIN and (not self.actor or not self.actor.is_superuser):
            raise forms.ValidationError("Admin faqat Super Admin yaratishi mumkin.")
        return role


class AdminUserUpdateForm(forms.Form):
    full_name = forms.CharField(label="To‘liq ism", max_length=150)
    username = forms.CharField(
        label="Login (username)",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        help_text="Email orqali ham kirish mumkin.",
    )
    phone = forms.CharField(label="Telefon", max_length=30, required=False)
    role = forms.ChoiceField(label="Role", choices=Role.choices)
    is_active = forms.BooleanField(label="Aktiv", required=False)

    def __init__(self, *args, actor=None, target_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        self.target_user = target_user
        if actor and not actor.is_superuser:
            self.fields["role"].choices = [
                (Role.STUDENT, "Student"),
                (Role.TEACHER, "Teacher"),
            ]

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        qs = User.objects.filter(username__iexact=username)
        if self.target_user:
            qs = qs.exclude(pk=self.target_user.pk)
        if qs.exists():
            raise forms.ValidationError("Bu username band.")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            return email
        qs = User.objects.filter(email__iexact=email)
        if self.target_user:
            qs = qs.exclude(pk=self.target_user.pk)
        if qs.exists():
            raise forms.ValidationError("Bu email band.")
        return email

    def clean_role(self):
        role = self.cleaned_data["role"]
        if role == Role.ADMIN and (not self.actor or not self.actor.is_superuser):
            raise forms.ValidationError("Role=Admin faqat Super Admin qo‘ya oladi.")
        if (
            self.target_user
            and self.target_user.is_superuser
            and self.actor
            and self.actor.pk == self.target_user.pk
            and role != Role.ADMIN
        ):
            raise forms.ValidationError("O‘zingizni Super Adminlikdan chiqara olmaysiz.")
        return role


class AdminSetPasswordForm(forms.Form):
    temporary_password = forms.CharField(
        label="Yangi vaqtinchalik parol",
        widget=forms.PasswordInput,
        min_length=4,
    )


courses = forms.ModelMultipleChoiceField(
    label="Kursga biriktirish (Student uchun)",
    queryset=Course.objects.all().order_by("title"),
    required=False,
    widget=forms.SelectMultiple(attrs={"size": 6}),
    help_text=(
        "Faqat role=Student bo‘lsa ishlaydi. Tanlangan kurslarga student "
        "avtomatik ro‘yxatga olinadi (Enrollment yaratiladi)."
    ),
)
