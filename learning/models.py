from django.conf import settings
from django.db import models


class Teacher(models.Model):
    full_name = models.CharField(max_length=150)
    specialty = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="teachers/", blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    show_on_landing = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teacher_profile",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "full_name"]
        verbose_name = "O‘qituvchi"
        verbose_name_plural = "O‘qituvchilar"

    def __str__(self):
        return self.full_name


class Subject(models.Model):
    """Fan."""

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Fan"
        verbose_name_plural = "Fanlar"

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to="courses/", blank=True, null=True)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
    )
    duration = models.CharField(max_length=80, blank=True)
    is_published = models.BooleanField(default=False, db_index=True)
    show_on_landing = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Modul"
        verbose_name_plural = "Modullar"

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=150)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    duration_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Dars"
        verbose_name_plural = "Darslar"

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    is_active = models.BooleanField(default=True, db_index=True)
    progress_percent = models.PositiveIntegerField(default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-enrolled_at"]
        verbose_name = "Ro‘yxatga olish"
        verbose_name_plural = "Ro‘yxatga olishlar"

    def __str__(self):
        return f"{self.student} → {self.course}"


class LessonProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress_rows")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("student", "lesson")
        verbose_name = "Dars progressi"
        verbose_name_plural = "Dars progresslari"


class Homework(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="homeworks",
        null=True,
        blank=True,
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="homeworks")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Uy vazifa"
        verbose_name_plural = "Uy vazifalar"

    def __str__(self):
        return self.title


class HomeworkSubmission(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Topshirildi"
        GRADED = "graded", "Baholandi"
        REJECTED = "rejected", "Qaytarildi"

    homework = models.ForeignKey(
        Homework, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="homework_submissions",
    )
    answer_text = models.TextField(blank=True)
    attachment = models.FileField(upload_to="homework/", blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SUBMITTED
    )
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("homework", "student")
        ordering = ["-submitted_at"]
        verbose_name = "Uy vazifa javobi"
        verbose_name_plural = "Uy vazifa javoblari"


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes")
    module = models.ForeignKey(
        Module, on_delete=models.SET_NULL, null=True, blank=True, related_name="quizzes"
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    time_limit_minutes = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Quiz"
        verbose_name_plural = "Quizlar"

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["sort_order", "id"]


class QuizChoice(models.Model):
    question = models.ForeignKey(
        QuizQuestion, on_delete=models.CASCADE, related_name="choices"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-started_at"]


class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="exams")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    time_limit_minutes = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Imtihon"
        verbose_name_plural = "Imtihonlar"

    def __str__(self):
        return self.title


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["sort_order", "id"]


class ExamChoice(models.Model):
    question = models.ForeignKey(
        ExamQuestion, on_delete=models.CASCADE, related_name="choices"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)


class ExamAttempt(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_attempts",
    )
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-started_at"]


class Certificate(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="certificates"
    )
    title = models.CharField(max_length=200)
    certificate_code = models.CharField(max_length=64, unique=True)
    issued_at = models.DateField(auto_now_add=True)
    file = models.FileField(upload_to="certificates/", blank=True, null=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-issued_at"]
        verbose_name = "Sertifikat"
        verbose_name_plural = "Sertifikatlar"

    def __str__(self):
        return f"{self.student} — {self.title}"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Bildirishnoma"
        verbose_name_plural = "Bildirishnomalar"

    def __str__(self):
        return self.title
