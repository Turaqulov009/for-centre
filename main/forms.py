from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction

from .models import Attendance, Course, Lead, Profile, SiteSettings, StudyGroup

User = get_user_model()


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["name", "phone", "course", "note"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Ismingizni yozing",
                    "autocomplete": "name",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "+998 __ ___ __ __",
                    "autocomplete": "tel",
                    "type": "tel",
                }
            ),
            "course": forms.TextInput(attrs={"placeholder": "Kurs nomi"}),
            "note": forms.Textarea(attrs={"rows": 3, "placeholder": "Izoh"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) < 9:
            raise forms.ValidationError("Telefon raqamini to‘g‘ri kiriting.")
        return phone


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Login",
        widget=forms.TextInput(
            attrs={"placeholder": "Login", "autocomplete": "username"}
        ),
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Parol", "autocomplete": "current-password"}
        ),
    )


class UserCreateForm(forms.Form):
    full_name = forms.CharField(label="To‘liq ism", max_length=150)
    username = forms.CharField(label="Login", max_length=150)
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput,
        min_length=4,
    )
    phone = forms.CharField(label="Telefon", max_length=30, required=False)
    role = forms.ChoiceField(
        label="Rol",
        choices=[
            (Profile.Role.STUDENT, "Student"),
            (Profile.Role.TEACHER, "O‘qituvchi"),
            (Profile.Role.ADMIN, "Admin"),
        ],
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Bu login band.")
        return username

    @transaction.atomic
    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
        )
        profile = user.profile
        profile.full_name = self.cleaned_data["full_name"]
        profile.phone = self.cleaned_data.get("phone", "")
        profile.role = self.cleaned_data["role"]
        profile.save()
        if profile.role == Profile.Role.ADMIN:
            user.is_staff = True
            user.save(update_fields=["is_staff"])
        return user


class UserPasswordForm(forms.Form):
    password = forms.CharField(
        label="Yangi parol",
        widget=forms.PasswordInput,
        min_length=4,
    )


class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ["name", "course_name", "teacher", "students", "is_active"]
        widgets = {
            "students": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teacher"].queryset = User.objects.filter(
            profile__role=Profile.Role.TEACHER,
            profile__is_active_member=True,
        )
        self.fields["students"].queryset = User.objects.filter(
            profile__role=Profile.Role.STUDENT,
            profile__is_active_member=True,
        )
        self.fields["teacher"].required = False


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            "hero_title",
            "hero_text",
            "phone",
            "telegram",
            "address",
            "work_time",
        ]
        widgets = {
            "hero_text": forms.Textarea(attrs={"rows": 3}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "category",
            "description",
            "duration",
            "is_published",
            "sort_order",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class AttendanceTakeForm(forms.Form):
    date = forms.DateField(
        label="Sana",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, students=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.students = students or []
        for student in self.students:
            self.fields[f"status_{student.id}"] = forms.ChoiceField(
                label=student.profile.display_name,
                choices=Attendance.Status.choices,
                initial=Attendance.Status.PRESENT,
            )
            self.fields[f"note_{student.id}"] = forms.CharField(
                label="Izoh",
                required=False,
                max_length=255,
                widget=forms.TextInput(attrs={"placeholder": "Izoh"}),
            )
