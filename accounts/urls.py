from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("verify-email/", views.verify_email_gate, name="verify_email_gate"),
    path(
        "verify-email/<str:token>/",
        views.verify_email_confirm,
        name="verify_email_confirm",
    ),
    path("password/forgot/", views.forgot_password, name="forgot_password"),
    path(
        "password/reset/<str:token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path(
        "password/change-required/",
        views.force_password_change,
        name="force_password_change",
    ),
]
