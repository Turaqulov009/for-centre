from django.contrib import admin

from .models import (
    EmailVerificationToken,
    PasswordResetToken,
    Profile,
    StudentProfile,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "role", "is_email_verified", "phone")
    list_filter = ("role", "is_email_verified")
    search_fields = ("full_name", "user__username", "user__email", "phone")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_graduated", "created_at")
    list_filter = ("is_graduated",)
    search_fields = ("user__username", "user__email")


admin.site.register(EmailVerificationToken)
admin.site.register(PasswordResetToken)
