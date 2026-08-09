from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from accounts.permissions import (
    admin_required,
    role_home_url_name,
    teacher_required,
)
from cms.forms import LeadForm
from cms.models import FAQ, Banner, Feature, News, SiteSettings
from learning.models import Course, Teacher
from learning.services import platform_statistics

from . import users as users_views
from . import cms_admin as cms_views
from . import learning_admin as learning_views
from . import assessments_admin as assessments_views
from . import student_panel as student_views


@require_http_methods(["GET", "POST"])
def landing(request):
    site = SiteSettings.get_solo()
    form = LeadForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Arizangiz qabul qilindi.")
        return redirect("/#contact")

    context = {
        "site": site,
        "form": form,
        "banners": Banner.objects.filter(is_active=True),
        "courses": Course.objects.filter(is_published=True, show_on_landing=True),
        "features": Feature.objects.filter(is_active=True),
        "teachers": Teacher.objects.filter(is_active=True, show_on_landing=True),
        "news_list": News.objects.filter(is_published=True)[:6],
        "faqs": FAQ.objects.filter(is_active=True),
        "stats": platform_statistics(),
    }
    return render(request, "portal/landing.html", context)


def portal_home(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    return redirect(role_home_url_name(request.user))


@admin_required
def admin_dashboard(request):
    return render(
        request,
        "portal/admin/dashboard.html",
        {"stats": platform_statistics()},
    )


@teacher_required
def teacher_dashboard(request):
    return render(request, "portal/teacher/dashboard.html")


# Student panel
student_dashboard = student_views.student_dashboard
student_profile = student_views.student_profile
student_courses = student_views.student_courses
student_course_detail = student_views.student_course_detail
student_lesson_detail = student_views.student_lesson_detail
student_lesson_complete = student_views.student_lesson_complete
student_homeworks = student_views.student_homeworks
student_homework_detail = student_views.student_homework_detail
student_quizzes = student_views.student_quizzes
student_quiz_take = student_views.student_quiz_take
student_quiz_result = student_views.student_quiz_result
student_exams = student_views.student_exams
student_exam_take = student_views.student_exam_take
student_exam_result = student_views.student_exam_result
student_results = student_views.student_results
student_progress = student_views.student_progress
student_certificates = student_views.student_certificates
student_notifications = student_views.student_notifications
student_notification_read = student_views.student_notification_read
student_notifications_read_all = student_views.student_notifications_read_all


# Users management (admin only)
admin_users = users_views.admin_users
admin_user_create = users_views.admin_user_create
admin_user_edit = users_views.admin_user_edit
admin_user_password = users_views.admin_user_password
admin_user_toggle = users_views.admin_user_toggle

# CMS management (admin only)
admin_settings = cms_views.admin_settings
admin_banners = cms_views.admin_banners
admin_banner_create = cms_views.admin_banner_create
admin_banner_edit = cms_views.admin_banner_edit
admin_banner_delete = cms_views.admin_banner_delete
admin_features = cms_views.admin_features
admin_feature_create = cms_views.admin_feature_create
admin_feature_edit = cms_views.admin_feature_edit
admin_feature_delete = cms_views.admin_feature_delete
admin_news = cms_views.admin_news
admin_news_create = cms_views.admin_news_create
admin_news_edit = cms_views.admin_news_edit
admin_news_delete = cms_views.admin_news_delete
admin_faqs = cms_views.admin_faqs
admin_faq_create = cms_views.admin_faq_create
admin_faq_edit = cms_views.admin_faq_edit
admin_faq_delete = cms_views.admin_faq_delete
admin_leads = cms_views.admin_leads
admin_lead_toggle = cms_views.admin_lead_toggle
admin_lead_delete = cms_views.admin_lead_delete

# Learning management (admin only)
admin_subjects = learning_views.admin_subjects
admin_subject_create = learning_views.admin_subject_create
admin_subject_edit = learning_views.admin_subject_edit
admin_subject_delete = learning_views.admin_subject_delete
admin_teachers = learning_views.admin_teachers
admin_teacher_create = learning_views.admin_teacher_create
admin_teacher_edit = learning_views.admin_teacher_edit
admin_teacher_delete = learning_views.admin_teacher_delete
admin_courses = learning_views.admin_courses
admin_course_create = learning_views.admin_course_create
admin_course_edit = learning_views.admin_course_edit
admin_course_delete = learning_views.admin_course_delete
admin_course_modules = learning_views.admin_course_modules
admin_module_create = learning_views.admin_module_create
admin_module_edit = learning_views.admin_module_edit
admin_module_delete = learning_views.admin_module_delete
admin_module_lessons = learning_views.admin_module_lessons
admin_lesson_create = learning_views.admin_lesson_create
admin_lesson_edit = learning_views.admin_lesson_edit
admin_lesson_delete = learning_views.admin_lesson_delete
admin_enrollments = learning_views.admin_enrollments
admin_enrollment_create = learning_views.admin_enrollment_create
admin_enrollment_edit = learning_views.admin_enrollment_edit
admin_enrollment_delete = learning_views.admin_enrollment_delete

# Assessments (admin only)
admin_homeworks = assessments_views.admin_homeworks
admin_homework_create = assessments_views.admin_homework_create
admin_homework_edit = assessments_views.admin_homework_edit
admin_homework_delete = assessments_views.admin_homework_delete
admin_quizzes = assessments_views.admin_quizzes
admin_quiz_create = assessments_views.admin_quiz_create
admin_quiz_edit = assessments_views.admin_quiz_edit
admin_quiz_delete = assessments_views.admin_quiz_delete
admin_quiz_questions = assessments_views.admin_quiz_questions
admin_quiz_question_create = assessments_views.admin_quiz_question_create
admin_quiz_question_edit = assessments_views.admin_quiz_question_edit
admin_quiz_question_delete = assessments_views.admin_quiz_question_delete
admin_exams = assessments_views.admin_exams
admin_exam_create = assessments_views.admin_exam_create
admin_exam_edit = assessments_views.admin_exam_edit
admin_exam_delete = assessments_views.admin_exam_delete
admin_exam_questions = assessments_views.admin_exam_questions
admin_exam_question_create = assessments_views.admin_exam_question_create
admin_exam_question_edit = assessments_views.admin_exam_question_edit
admin_exam_question_delete = assessments_views.admin_exam_question_delete
admin_certificates = assessments_views.admin_certificates
admin_certificate_create = assessments_views.admin_certificate_create
admin_certificate_edit = assessments_views.admin_certificate_edit
admin_certificate_delete = assessments_views.admin_certificate_delete
admin_notifications = assessments_views.admin_notifications
admin_notification_create = assessments_views.admin_notification_create
admin_notification_delete = assessments_views.admin_notification_delete
