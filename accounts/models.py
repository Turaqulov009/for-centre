from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    TEACHER = "teacher", "Teacher"
    STUDENT = "student", "Student"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True,
    )
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    must_change_password = models.BooleanField(
        default=True,
        help_text="Birinchi kirishda yangi parol o‘rnatish majburiy",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name", "user__username"]
        verbose_name = "Profil"
        verbose_name_plural = "Profillar"

    def __str__(self):
        return f"{self.display_name} ({self.get_role_display()})"

    @property
    def display_name(self):
        return self.full_name or self.user.get_full_name() or self.user.username

    @property
    def is_admin(self):
        return self.role == Role.ADMIN or self.user.is_superuser

    @property
    def is_teacher(self):
        return self.role == Role.TEACHER and not self.user.is_superuser

    @property
    def is_student(self):
        return self.role == Role.STUDENT and not self.user.is_superuser


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    is_graduated = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Bitiruvchi sifatida statistika uchun",
    )
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student profili"
        verbose_name_plural = "Student profillari"

    def __str__(self):
        return f"Student: {self.user.username}"


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_tokens",
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Email token for {self.user_id}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Password reset for {self.user_id}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_user_profiles(sender, instance, created, **kwargs):
    if created:
        role = Role.ADMIN if instance.is_superuser else Role.STUDENT
        Profile.objects.create(
            user=instance,
            role=role,
            full_name=instance.get_full_name() or instance.username,
            is_email_verified=instance.is_superuser,
            must_change_password=not instance.is_superuser,
        )
        if role == Role.STUDENT:
            StudentProfile.objects.create(user=instance)
        return

    profile, _ = Profile.objects.get_or_create(
        user=instance,
        defaults={
            "role": Role.ADMIN if instance.is_superuser else Role.STUDENT,
            "full_name": instance.get_full_name() or instance.username,
            "must_change_password": not instance.is_superuser,
        },
    )
    if instance.is_superuser and profile.role != Role.ADMIN:
        profile.role = Role.ADMIN
        profile.is_email_verified = True
        profile.must_change_password = False
        profile.save(update_fields=["role", "is_email_verified", "must_change_password"])
