from django.contrib import admin

from .models import Attendance, Course, Lead, Profile, SiteSettings, StudyGroup


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "course", "is_contacted", "created_at")
    list_filter = ("is_contacted", "created_at")
    search_fields = ("name", "phone", "note", "course")
    list_editable = ("is_contacted",)
    readonly_fields = ("created_at",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("__str__", "phone", "telegram", "updated_at")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("title", "category", "description")
    list_editable = ("is_published", "sort_order")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "role", "phone", "is_active_member")
    list_filter = ("role", "is_active_member")
    search_fields = ("full_name", "user__username", "phone")


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "course_name", "teacher", "is_active")
    list_filter = ("is_active", "course_name")
    filter_horizontal = ("students",)
    search_fields = ("name", "course_name")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("date", "group", "student", "status", "marked_by")
    list_filter = ("status", "date", "group")
    search_fields = ("student__username", "student__profile__full_name")
