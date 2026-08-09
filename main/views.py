from datetime import date

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .decorators import admin_required, student_required, teacher_required
from .forms import (
    AttendanceTakeForm,
    CourseForm,
    LeadForm,
    LoginForm,
    SiteSettingsForm,
    StudyGroupForm,
    UserCreateForm,
    UserPasswordForm,
)
from .models import Attendance, Course, Lead, Profile, SiteSettings, StudyGroup


def _portal_redirect(user):
    profile = getattr(user, "profile", None)
    if profile is None:
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={
                "role": Profile.Role.ADMIN if user.is_superuser else Profile.Role.STUDENT,
                "full_name": user.get_full_name() or user.username,
            },
        )
    if profile.is_admin:
        return redirect("admin_dashboard")
    if profile.is_teacher:
        return redirect("teacher_dashboard")
    return redirect("student_dashboard")


@require_http_methods(["GET", "POST"])
def home(request):
    site = SiteSettings.get_solo()
    courses = Course.objects.filter(is_published=True)

    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rahmat! Tez orada siz bilan bog‘lanamiz.")
            return redirect("/#contact")
        messages.error(request, "Iltimos, majburiy maydonlarni to‘g‘ri to‘ldiring.")
    else:
        form = LeadForm()

    return render(
        request,
        "main/home.html",
        {"form": form, "site": site, "courses": courses},
    )


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return _portal_redirect(request.user)

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Xush kelibsiz!")
        return _portal_redirect(request.user)

    return render(request, "portal/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect("login")


@login_required
def portal_home(request):
    return _portal_redirect(request.user)


# -------- Admin --------


@admin_required
def admin_dashboard(request):
    context = {
        "students_count": Profile.objects.filter(role=Profile.Role.STUDENT).count(),
        "teachers_count": Profile.objects.filter(role=Profile.Role.TEACHER).count(),
        "groups_count": StudyGroup.objects.filter(is_active=True).count(),
        "leads_count": Lead.objects.filter(is_contacted=False).count(),
        "courses_count": Course.objects.count(),
        "recent_users": Profile.objects.select_related("user").exclude(
            role=Profile.Role.ADMIN
        )[:8],
        "recent_attendance": Attendance.objects.select_related(
            "student", "group", "marked_by"
        )[:8],
    }
    return render(request, "portal/admin/dashboard.html", context)


@admin_required
@require_http_methods(["GET", "POST"])
def admin_site(request):
    site = SiteSettings.get_solo()
    form = SiteSettingsForm(request.POST or None, instance=site)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sayt ma’lumotlari saqlandi.")
        return redirect("admin_site")
    return render(request, "portal/admin/site.html", {"form": form})


@admin_required
@require_http_methods(["GET", "POST"])
def admin_courses(request):
    form = CourseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kurs qo‘shildi.")
        return redirect("admin_courses")
    courses = Course.objects.all()
    return render(
        request,
        "portal/admin/courses.html",
        {"form": form, "courses": courses},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_course_edit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    form = CourseForm(request.POST or None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kurs yangilandi.")
        return redirect("admin_courses")
    return render(
        request,
        "portal/admin/course_edit.html",
        {"form": form, "course": course},
    )


@admin_required
def admin_course_delete(request, course_id):
    if request.method != "POST":
        return redirect("admin_courses")
    course = get_object_or_404(Course, pk=course_id)
    course.delete()
    messages.success(request, "Kurs o‘chirildi.")
    return redirect("admin_courses")


@admin_required
def admin_leads(request):
    leads = Lead.objects.all()
    return render(request, "portal/admin/leads.html", {"leads": leads})


@admin_required
def admin_lead_toggle(request, lead_id):
    if request.method != "POST":
        return redirect("admin_leads")
    lead = get_object_or_404(Lead, pk=lead_id)
    lead.is_contacted = not lead.is_contacted
    lead.save(update_fields=["is_contacted"])
    return redirect("admin_leads")


@admin_required
@require_http_methods(["GET", "POST"])
def admin_users(request):
    form = UserCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(
            request,
            f"Foydalanuvchi yaratildi: {user.username} ({user.profile.get_role_display()})",
        )
        return redirect("admin_users")

    profiles = Profile.objects.select_related("user").all()
    return render(
        request,
        "portal/admin/users.html",
        {"form": form, "profiles": profiles},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_user_password(request, user_id):
    profile = get_object_or_404(Profile.objects.select_related("user"), user_id=user_id)
    form = UserPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        profile.user.set_password(form.cleaned_data["password"])
        profile.user.save()
        messages.success(request, f"{profile.display_name} uchun yangi parol o‘rnatildi.")
        return redirect("admin_users")
    return render(
        request,
        "portal/admin/user_password.html",
        {"form": form, "profile": profile},
    )


@admin_required
def admin_toggle_user(request, user_id):
    if request.method != "POST":
        return redirect("admin_users")
    profile = get_object_or_404(Profile, user_id=user_id)
    if profile.user_id == request.user.id:
        messages.error(request, "O‘zingizni o‘chira olmaysiz.")
        return redirect("admin_users")
    profile.is_active_member = not profile.is_active_member
    profile.user.is_active = profile.is_active_member
    profile.save(update_fields=["is_active_member"])
    profile.user.save(update_fields=["is_active"])
    state = "yoqildi" if profile.is_active_member else "o‘chirildi"
    messages.success(request, f"{profile.display_name} {state}.")
    return redirect("admin_users")


@admin_required
@require_http_methods(["GET", "POST"])
def admin_groups(request):
    form = StudyGroupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Guruh yaratildi.")
        return redirect("admin_groups")
    groups = StudyGroup.objects.select_related("teacher").prefetch_related("students")
    return render(
        request,
        "portal/admin/groups.html",
        {"form": form, "groups": groups},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_group_edit(request, group_id):
    group = get_object_or_404(StudyGroup, pk=group_id)
    form = StudyGroupForm(request.POST or None, instance=group)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Guruh yangilandi.")
        return redirect("admin_groups")
    return render(
        request,
        "portal/admin/group_edit.html",
        {"form": form, "group": group},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_attendance(request):
    groups = StudyGroup.objects.filter(is_active=True).order_by("name")
    group_id = request.GET.get("group") or request.POST.get("group")
    selected_group = None
    form = None

    if group_id:
        selected_group = get_object_or_404(groups, pk=group_id)
        students = list(selected_group.students.filter(is_active=True).select_related("profile"))
        selected_date = request.GET.get("date") or request.POST.get("date") or str(date.today())
        initial = {"date": selected_date}
        existing = {
            row.student_id: row
            for row in Attendance.objects.filter(group=selected_group, date=selected_date)
        }

        form = AttendanceTakeForm(
            request.POST or None,
            students=students,
            initial=initial,
        )

        if request.method == "GET" and existing:
            for student in students:
                row = existing.get(student.id)
                if row:
                    form.fields[f"status_{student.id}"].initial = row.status
                    form.fields[f"note_{student.id}"].initial = row.note

        if request.method == "POST" and form.is_valid():
            day = form.cleaned_data["date"]
            for student in students:
                status = form.cleaned_data[f"status_{student.id}"]
                note = form.cleaned_data.get(f"note_{student.id}", "")
                Attendance.objects.update_or_create(
                    group=selected_group,
                    student=student,
                    date=day,
                    defaults={
                        "status": status,
                        "note": note,
                        "marked_by": request.user,
                    },
                )
            messages.success(request, "Yo‘qlama saqlandi.")
            return redirect(f"{request.path}?group={selected_group.id}&date={day}")

        rows = [
            {
                "student": student,
                "status": form[f"status_{student.id}"],
                "note": form[f"note_{student.id}"],
            }
            for student in students
        ]
    else:
        rows = []
        form = None
        selected_group = None

    history = Attendance.objects.select_related("student", "group", "student__profile")[:30]
    return render(
        request,
        "portal/admin/attendance.html",
        {
            "groups": groups,
            "selected_group": selected_group,
            "form": form,
            "rows": rows,
            "history": history,
        },
    )


# -------- Teacher --------


@teacher_required
def teacher_dashboard(request):
    if request.profile.is_admin:
        groups = StudyGroup.objects.filter(is_active=True)
    else:
        groups = StudyGroup.objects.filter(teacher=request.user, is_active=True)

    groups = groups.annotate(student_count=Count("students"))
    recent = Attendance.objects.filter(group__in=groups).select_related(
        "student", "group", "student__profile"
    )[:10]
    return render(
        request,
        "portal/teacher/dashboard.html",
        {"groups": groups, "recent": recent},
    )


@teacher_required
@require_http_methods(["GET", "POST"])
def teacher_attendance(request, group_id):
    if request.profile.is_admin:
        group = get_object_or_404(StudyGroup, pk=group_id, is_active=True)
    else:
        group = get_object_or_404(
            StudyGroup, pk=group_id, teacher=request.user, is_active=True
        )

    students = list(group.students.filter(is_active=True).select_related("profile"))
    initial = {"date": date.today()}
    selected_date = request.GET.get("date") or request.POST.get("date")
    if selected_date:
        initial["date"] = selected_date

    form = AttendanceTakeForm(request.POST or None, students=students, initial=initial)

    if request.method == "GET" and selected_date:
        existing = {
            row.student_id: row
            for row in Attendance.objects.filter(group=group, date=selected_date)
        }
        for student in students:
            row = existing.get(student.id)
            if row:
                form.fields[f"status_{student.id}"].initial = row.status
                form.fields[f"note_{student.id}"].initial = row.note

    if request.method == "POST" and form.is_valid():
        day = form.cleaned_data["date"]
        for student in students:
            Attendance.objects.update_or_create(
                group=group,
                student=student,
                date=day,
                defaults={
                    "status": form.cleaned_data[f"status_{student.id}"],
                    "note": form.cleaned_data.get(f"note_{student.id}", ""),
                    "marked_by": request.user,
                },
            )
        messages.success(request, "Yo‘qlama saqlandi.")
        return redirect("teacher_attendance", group_id=group.id)

    rows = [
        {
            "student": student,
            "status": form[f"status_{student.id}"],
            "note": form[f"note_{student.id}"],
        }
        for student in students
    ]
    history = (
        Attendance.objects.filter(group=group)
        .select_related("student", "student__profile")
        .order_by("-date")[:40]
    )
    return render(
        request,
        "portal/teacher/attendance.html",
        {
            "group": group,
            "form": form,
            "rows": rows,
            "history": history,
        },
    )


# -------- Student --------


@student_required
def student_dashboard(request):
    groups = request.user.study_groups.filter(is_active=True).select_related("teacher")
    attendances = (
        Attendance.objects.filter(student=request.user)
        .select_related("group")
        .order_by("-date")[:20]
    )
    stats = Attendance.objects.filter(student=request.user).aggregate(
        total=Count("id"),
        present=Count("id", filter=Q(status=Attendance.Status.PRESENT)),
        absent=Count("id", filter=Q(status=Attendance.Status.ABSENT)),
        late=Count("id", filter=Q(status=Attendance.Status.LATE)),
    )
    return render(
        request,
        "portal/student/dashboard.html",
        {"groups": groups, "attendances": attendances, "stats": stats},
    )
