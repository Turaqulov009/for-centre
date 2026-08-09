from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("portal/", views.portal_home, name="home"),
    path("portal/admin/", views.admin_dashboard, name="admin_dashboard"),
    # Users
    path("portal/admin/users/", views.admin_users, name="admin_users"),
    path("portal/admin/users/create/", views.admin_user_create, name="admin_user_create"),
    path(
        "portal/admin/users/<int:user_id>/edit/",
        views.admin_user_edit,
        name="admin_user_edit",
    ),
    path(
        "portal/admin/users/<int:user_id>/password/",
        views.admin_user_password,
        name="admin_user_password",
    ),
    path(
        "portal/admin/users/<int:user_id>/toggle/",
        views.admin_user_toggle,
        name="admin_user_toggle",
    ),
    # CMS
    path("portal/admin/settings/", views.admin_settings, name="admin_settings"),
    path("portal/admin/banners/", views.admin_banners, name="admin_banners"),
    path(
        "portal/admin/banners/create/",
        views.admin_banner_create,
        name="admin_banner_create",
    ),
    path(
        "portal/admin/banners/<int:pk>/edit/",
        views.admin_banner_edit,
        name="admin_banner_edit",
    ),
    path(
        "portal/admin/banners/<int:pk>/delete/",
        views.admin_banner_delete,
        name="admin_banner_delete",
    ),
    path("portal/admin/features/", views.admin_features, name="admin_features"),
    path(
        "portal/admin/features/create/",
        views.admin_feature_create,
        name="admin_feature_create",
    ),
    path(
        "portal/admin/features/<int:pk>/edit/",
        views.admin_feature_edit,
        name="admin_feature_edit",
    ),
    path(
        "portal/admin/features/<int:pk>/delete/",
        views.admin_feature_delete,
        name="admin_feature_delete",
    ),
    path("portal/admin/news/", views.admin_news, name="admin_news"),
    path("portal/admin/news/create/", views.admin_news_create, name="admin_news_create"),
    path(
        "portal/admin/news/<int:pk>/edit/",
        views.admin_news_edit,
        name="admin_news_edit",
    ),
    path(
        "portal/admin/news/<int:pk>/delete/",
        views.admin_news_delete,
        name="admin_news_delete",
    ),
    path("portal/admin/faqs/", views.admin_faqs, name="admin_faqs"),
    path("portal/admin/faqs/create/", views.admin_faq_create, name="admin_faq_create"),
    path(
        "portal/admin/faqs/<int:pk>/edit/",
        views.admin_faq_edit,
        name="admin_faq_edit",
    ),
    path(
        "portal/admin/faqs/<int:pk>/delete/",
        views.admin_faq_delete,
        name="admin_faq_delete",
    ),
    path("portal/admin/leads/", views.admin_leads, name="admin_leads"),
    path(
        "portal/admin/leads/<int:pk>/toggle/",
        views.admin_lead_toggle,
        name="admin_lead_toggle",
    ),
    path(
        "portal/admin/leads/<int:pk>/delete/",
        views.admin_lead_delete,
        name="admin_lead_delete",
    ),
    # Learning
    path("portal/admin/subjects/", views.admin_subjects, name="admin_subjects"),
    path(
        "portal/admin/subjects/create/",
        views.admin_subject_create,
        name="admin_subject_create",
    ),
    path(
        "portal/admin/subjects/<int:pk>/edit/",
        views.admin_subject_edit,
        name="admin_subject_edit",
    ),
    path(
        "portal/admin/subjects/<int:pk>/delete/",
        views.admin_subject_delete,
        name="admin_subject_delete",
    ),
    path("portal/admin/teachers/", views.admin_teachers, name="admin_teachers"),
    path(
        "portal/admin/teachers/create/",
        views.admin_teacher_create,
        name="admin_teacher_create",
    ),
    path(
        "portal/admin/teachers/<int:pk>/edit/",
        views.admin_teacher_edit,
        name="admin_teacher_edit",
    ),
    path(
        "portal/admin/teachers/<int:pk>/delete/",
        views.admin_teacher_delete,
        name="admin_teacher_delete",
    ),
    path("portal/admin/courses/", views.admin_courses, name="admin_courses"),
    path(
        "portal/admin/courses/create/",
        views.admin_course_create,
        name="admin_course_create",
    ),
    path(
        "portal/admin/courses/<int:pk>/edit/",
        views.admin_course_edit,
        name="admin_course_edit",
    ),
    path(
        "portal/admin/courses/<int:pk>/delete/",
        views.admin_course_delete,
        name="admin_course_delete",
    ),
    path(
        "portal/admin/courses/<int:course_id>/modules/",
        views.admin_course_modules,
        name="admin_course_modules",
    ),
    path(
        "portal/admin/courses/<int:course_id>/modules/create/",
        views.admin_module_create,
        name="admin_module_create",
    ),
    path(
        "portal/admin/modules/<int:pk>/edit/",
        views.admin_module_edit,
        name="admin_module_edit",
    ),
    path(
        "portal/admin/modules/<int:pk>/delete/",
        views.admin_module_delete,
        name="admin_module_delete",
    ),
    path(
        "portal/admin/modules/<int:module_id>/lessons/",
        views.admin_module_lessons,
        name="admin_module_lessons",
    ),
    path(
        "portal/admin/modules/<int:module_id>/lessons/create/",
        views.admin_lesson_create,
        name="admin_lesson_create",
    ),
    path(
        "portal/admin/lessons/<int:pk>/edit/",
        views.admin_lesson_edit,
        name="admin_lesson_edit",
    ),
    path(
        "portal/admin/lessons/<int:pk>/delete/",
        views.admin_lesson_delete,
        name="admin_lesson_delete",
    ),
    path(
        "portal/admin/enrollments/",
        views.admin_enrollments,
        name="admin_enrollments",
    ),
    path(
        "portal/admin/enrollments/create/",
        views.admin_enrollment_create,
        name="admin_enrollment_create",
    ),
    path(
        "portal/admin/enrollments/<int:pk>/edit/",
        views.admin_enrollment_edit,
        name="admin_enrollment_edit",
    ),
    path(
        "portal/admin/enrollments/<int:pk>/delete/",
        views.admin_enrollment_delete,
        name="admin_enrollment_delete",
    ),
    # Homework
    path("portal/admin/homeworks/", views.admin_homeworks, name="admin_homeworks"),
    path(
        "portal/admin/homeworks/create/",
        views.admin_homework_create,
        name="admin_homework_create",
    ),
    path(
        "portal/admin/homeworks/<int:pk>/edit/",
        views.admin_homework_edit,
        name="admin_homework_edit",
    ),
    path(
        "portal/admin/homeworks/<int:pk>/delete/",
        views.admin_homework_delete,
        name="admin_homework_delete",
    ),
    # Quiz
    path("portal/admin/quizzes/", views.admin_quizzes, name="admin_quizzes"),
    path(
        "portal/admin/quizzes/create/",
        views.admin_quiz_create,
        name="admin_quiz_create",
    ),
    path(
        "portal/admin/quizzes/<int:pk>/edit/",
        views.admin_quiz_edit,
        name="admin_quiz_edit",
    ),
    path(
        "portal/admin/quizzes/<int:pk>/delete/",
        views.admin_quiz_delete,
        name="admin_quiz_delete",
    ),
    path(
        "portal/admin/quizzes/<int:quiz_id>/questions/",
        views.admin_quiz_questions,
        name="admin_quiz_questions",
    ),
    path(
        "portal/admin/quizzes/<int:quiz_id>/questions/create/",
        views.admin_quiz_question_create,
        name="admin_quiz_question_create",
    ),
    path(
        "portal/admin/quiz-questions/<int:pk>/edit/",
        views.admin_quiz_question_edit,
        name="admin_quiz_question_edit",
    ),
    path(
        "portal/admin/quiz-questions/<int:pk>/delete/",
        views.admin_quiz_question_delete,
        name="admin_quiz_question_delete",
    ),
    # Exam
    path("portal/admin/exams/", views.admin_exams, name="admin_exams"),
    path(
        "portal/admin/exams/create/",
        views.admin_exam_create,
        name="admin_exam_create",
    ),
    path(
        "portal/admin/exams/<int:pk>/edit/",
        views.admin_exam_edit,
        name="admin_exam_edit",
    ),
    path(
        "portal/admin/exams/<int:pk>/delete/",
        views.admin_exam_delete,
        name="admin_exam_delete",
    ),
    path(
        "portal/admin/exams/<int:exam_id>/questions/",
        views.admin_exam_questions,
        name="admin_exam_questions",
    ),
    path(
        "portal/admin/exams/<int:exam_id>/questions/create/",
        views.admin_exam_question_create,
        name="admin_exam_question_create",
    ),
    path(
        "portal/admin/exam-questions/<int:pk>/edit/",
        views.admin_exam_question_edit,
        name="admin_exam_question_edit",
    ),
    path(
        "portal/admin/exam-questions/<int:pk>/delete/",
        views.admin_exam_question_delete,
        name="admin_exam_question_delete",
    ),
    # Certificates
    path(
        "portal/admin/certificates/",
        views.admin_certificates,
        name="admin_certificates",
    ),
    path(
        "portal/admin/certificates/create/",
        views.admin_certificate_create,
        name="admin_certificate_create",
    ),
    path(
        "portal/admin/certificates/<int:pk>/edit/",
        views.admin_certificate_edit,
        name="admin_certificate_edit",
    ),
    path(
        "portal/admin/certificates/<int:pk>/delete/",
        views.admin_certificate_delete,
        name="admin_certificate_delete",
    ),
    # Notifications
    path(
        "portal/admin/notifications/",
        views.admin_notifications,
        name="admin_notifications",
    ),
    path(
        "portal/admin/notifications/create/",
        views.admin_notification_create,
        name="admin_notification_create",
    ),
    path(
        "portal/admin/notifications/<int:pk>/delete/",
        views.admin_notification_delete,
        name="admin_notification_delete",
    ),
    # Role dashboards
    path("portal/student/", views.student_dashboard, name="student_dashboard"),
    path("portal/student/profile/", views.student_profile, name="student_profile"),
    path("portal/student/courses/", views.student_courses, name="student_courses"),
    path(
        "portal/student/courses/<int:course_id>/",
        views.student_course_detail,
        name="student_course_detail",
    ),
    path(
        "portal/student/lessons/<int:lesson_id>/",
        views.student_lesson_detail,
        name="student_lesson_detail",
    ),
    path(
        "portal/student/lessons/<int:lesson_id>/complete/",
        views.student_lesson_complete,
        name="student_lesson_complete",
    ),
    path(
        "portal/student/homeworks/",
        views.student_homeworks,
        name="student_homeworks",
    ),
    path(
        "portal/student/homeworks/<int:pk>/",
        views.student_homework_detail,
        name="student_homework_detail",
    ),
    path("portal/student/quizzes/", views.student_quizzes, name="student_quizzes"),
    path(
        "portal/student/quizzes/<int:pk>/take/",
        views.student_quiz_take,
        name="student_quiz_take",
    ),
    path(
        "portal/student/quizzes/attempts/<int:attempt_id>/",
        views.student_quiz_result,
        name="student_quiz_result",
    ),
    path("portal/student/exams/", views.student_exams, name="student_exams"),
    path(
        "portal/student/exams/<int:pk>/take/",
        views.student_exam_take,
        name="student_exam_take",
    ),
    path(
        "portal/student/exams/attempts/<int:attempt_id>/",
        views.student_exam_result,
        name="student_exam_result",
    ),
    path("portal/student/results/", views.student_results, name="student_results"),
    path("portal/student/progress/", views.student_progress, name="student_progress"),
    path(
        "portal/student/certificates/",
        views.student_certificates,
        name="student_certificates",
    ),
    path(
        "portal/student/notifications/",
        views.student_notifications,
        name="student_notifications",
    ),
    path(
        "portal/student/notifications/<int:pk>/read/",
        views.student_notification_read,
        name="student_notification_read",
    ),
    path(
        "portal/student/notifications/read-all/",
        views.student_notifications_read_all,
        name="student_notifications_read_all",
    ),
    path("portal/teacher/", views.teacher_dashboard, name="teacher_dashboard"),
]