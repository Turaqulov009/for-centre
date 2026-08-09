from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("portal/", views.portal_home, name="portal_home"),
    # Admin only — barcha ma’lumotlar
    path("portal/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("portal/admin/site/", views.admin_site, name="admin_site"),
    path("portal/admin/courses/", views.admin_courses, name="admin_courses"),
    path(
        "portal/admin/courses/<int:course_id>/",
        views.admin_course_edit,
        name="admin_course_edit",
    ),
    path(
        "portal/admin/courses/<int:course_id>/delete/",
        views.admin_course_delete,
        name="admin_course_delete",
    ),
    path("portal/admin/users/", views.admin_users, name="admin_users"),
    path(
        "portal/admin/users/<int:user_id>/password/",
        views.admin_user_password,
        name="admin_user_password",
    ),
    path(
        "portal/admin/users/<int:user_id>/toggle/",
        views.admin_toggle_user,
        name="admin_toggle_user",
    ),
    path("portal/admin/groups/", views.admin_groups, name="admin_groups"),
    path(
        "portal/admin/groups/<int:group_id>/",
        views.admin_group_edit,
        name="admin_group_edit",
    ),
    path("portal/admin/attendance/", views.admin_attendance, name="admin_attendance"),
    path("portal/admin/leads/", views.admin_leads, name="admin_leads"),
    path(
        "portal/admin/leads/<int:lead_id>/toggle/",
        views.admin_lead_toggle,
        name="admin_lead_toggle",
    ),
    # Teacher — faqat yo‘qlama
    path("portal/teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path(
        "portal/teacher/groups/<int:group_id>/attendance/",
        views.teacher_attendance,
        name="teacher_attendance",
    ),
    # Student — faqat ko‘rish
    path("portal/student/", views.student_dashboard, name="student_dashboard"),
]
