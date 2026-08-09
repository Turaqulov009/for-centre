from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Lead(models.Model):
    name = models.CharField("Ism", max_length=120)
    phone = models.CharField("Telefon", max_length=30)
    course = models.CharField("Kurs", max_length=120, blank=True)
    note = models.TextField("Izoh", blank=True)
    created_at = models.DateTimeField("Yuborilgan vaqt", auto_now_add=True)
    is_contacted = models.BooleanField("Bog‘lanildi", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ariza"
        verbose_name_plural = "Arizalar"

    def __str__(self):
        return f"{self.name} — {self.course}"


class SiteSettings(models.Model):
    hero_title = models.CharField("Bosh sarlavha", max_length=200, blank=True)
    hero_text = models.TextField("Bosh matn", blank=True)
    phone = models.CharField("Telefon", max_length=50, blank=True)
    telegram = models.CharField("Telegram", max_length=100, blank=True)
    address = models.CharField("Manzil", max_length=255, blank=True)
    work_time = models.CharField("Ish vaqti", max_length=120, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sayt sozlamasi"
        verbose_name_plural = "Sayt sozlamalari"

    def __str__(self):
        return "Sayt ma’lumotlari"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Course(models.Model):
    title = models.CharField("Kurs nomi", max_length=150)
    category = models.CharField("Kategoriya", max_length=80, blank=True)
    description = models.TextField("Tavsif", blank=True)
    duration = models.CharField("Davomiyligi", max_length=80, blank=True)
    is_published = models.BooleanField("Saytda ko‘rsatish", default=True)
    sort_order = models.PositiveIntegerField("Tartib", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"

    def __str__(self):
        return self.title


class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        TEACHER = "teacher", "O‘qituvchi"
        STUDENT = "student", "Student"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        "Rol",
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    phone = models.CharField("Telefon", max_length=30, blank=True)
    full_name = models.CharField("To‘liq ism", max_length=150, blank=True)
    is_active_member = models.BooleanField("Faol", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
        return self.role == self.Role.ADMIN or self.user.is_superuser

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT


class StudyGroup(models.Model):
    name = models.CharField("Guruh nomi", max_length=120)
    course_name = models.CharField("Kurs", max_length=120)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teaching_groups",
        limit_choices_to={"profile__role": Profile.Role.TEACHER},
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="study_groups",
        blank=True,
        limit_choices_to={"profile__role": Profile.Role.STUDENT},
    )
    is_active = models.BooleanField("Faol", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"

    def __str__(self):
        return f"{self.name} — {self.course_name}"


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Keldi"
        ABSENT = "absent", "Kelmadi"
        LATE = "late", "Kechikdi"
        EXCUSED = "excused", "Sababli"

    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendances",
        limit_choices_to={"profile__role": Profile.Role.STUDENT},
    )
    date = models.DateField("Sana")
    status = models.CharField(
        "Holat",
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT,
    )
    note = models.CharField("Izoh", max_length=255, blank=True)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_attendances",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "student__username"]
        unique_together = ("group", "student", "date")
        verbose_name = "Yo‘qlama"
        verbose_name_plural = "Yo‘qlamalar"

    def __str__(self):
        return f"{self.student} — {self.date} — {self.get_status_display()}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        role = Profile.Role.ADMIN if instance.is_superuser else Profile.Role.STUDENT
        Profile.objects.create(
            user=instance,
            role=role,
            full_name=instance.get_full_name() or instance.username,
        )
    else:
        profile, _ = Profile.objects.get_or_create(
            user=instance,
            defaults={
                "role": Profile.Role.ADMIN if instance.is_superuser else Profile.Role.STUDENT,
                "full_name": instance.get_full_name() or instance.username,
            },
        )
        if instance.is_superuser and profile.role != Profile.Role.ADMIN:
            profile.role = Profile.Role.ADMIN
            profile.save(update_fields=["role"])
