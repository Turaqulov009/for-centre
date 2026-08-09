from django.contrib import admin

from . import models


@admin.register(models.Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("full_name", "specialty", "is_active", "show_on_landing", "sort_order")
    list_filter = ("is_active", "show_on_landing")
    search_fields = ("full_name", "specialty", "email")


@admin.register(models.Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active")
    search_fields = ("title",)


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subject",
        "teacher",
        "is_published",
        "show_on_landing",
        "sort_order",
    )
    list_filter = ("is_published", "show_on_landing", "subject")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "short_description")


@admin.register(models.Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "sort_order", "is_published")
    list_filter = ("course",)


@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "sort_order", "is_published")
    list_filter = ("module__course",)


@admin.register(models.Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "is_active", "progress_percent", "enrolled_at")
    list_filter = ("is_active", "course")


@admin.register(models.Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "due_date", "is_published")
    list_filter = ("course", "is_published")


@admin.register(models.HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ("homework", "student", "status", "score", "submitted_at")
    list_filter = ("status",)


@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "is_published", "created_at")


@admin.register(models.Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "is_published", "created_at")


@admin.register(models.Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "course", "certificate_code", "issued_at")
    search_fields = ("certificate_code", "student__username")


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "is_read", "created_at")
    list_filter = ("is_read",)


admin.site.register(models.LessonProgress)
admin.site.register(models.QuizQuestion)
admin.site.register(models.QuizChoice)
admin.site.register(models.QuizAttempt)
admin.site.register(models.ExamQuestion)
admin.site.register(models.ExamChoice)
admin.site.register(models.ExamAttempt)
