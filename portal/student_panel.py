from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import StudentProfile
from accounts.permissions import student_required
from cms.models import News
from learning.models import (
    Certificate,
    Enrollment,
    Exam,
    ExamAttempt,
    Homework,
    HomeworkSubmission,
    Lesson,
    LessonProgress,
    Notification,
    Quiz,
    QuizAttempt,
)
from learning import services as learning_services

from .student_forms import HomeworkSubmitForm, StudentProfileForm


def _render(request, template, context=None):
    ctx = context or {}
    ctx.setdefault(
        "unread_count",
        Notification.objects.filter(recipient=request.user, is_read=False).count(),
    )
    if "top_progress" not in ctx:
        if "stats" in ctx and isinstance(ctx["stats"], dict):
            ctx["top_progress"] = ctx["stats"].get("avg_progress", 0)
        else:
            ctx["top_progress"] = learning_services._avg_progress(request.user)
    return render(request, template, ctx)


def _course_ids(request):
    return learning_services.student_course_ids(request.user)


@student_required
def student_dashboard(request):
    course_ids = learning_services.student_course_ids(request.user)
    enrollments = list(learning_services.student_enrollments(request.user)[:8])
    homeworks = list(
        Homework.objects.filter(course_id__in=course_ids, is_published=True)
        .select_related("course")
        .order_by("due_date", "-created_at")[:6]
    )
    submitted_ids = set(
        HomeworkSubmission.objects.filter(
            student=request.user, homework_id__in=[h.pk for h in homeworks]
        ).values_list("homework_id", flat=True)
    )
    homework_rows = [
        {"homework": hw, "done": hw.pk in submitted_ids} for hw in homeworks
    ]

    return _render(
        request,
        "portal/student/dashboard.html",
        {
            "stats": learning_services.student_dashboard_stats(request.user),
            "enrollments": enrollments,
            "homework_rows": homework_rows,
            "notifications": Notification.objects.filter(recipient=request.user)[:5],
            "news_list": News.objects.filter(is_published=True)[:4],
        },
    )


@student_required
@require_http_methods(["GET", "POST"])
def student_profile(request):
    profile = request.profile
    student, _ = StudentProfile.objects.get_or_create(user=request.user)
    initial = {
        "full_name": profile.full_name,
        "phone": profile.phone,
        "bio": student.bio,
        "date_of_birth": student.date_of_birth,
    }
    form = StudentProfileForm(
        request.POST or None,
        request.FILES or None,
        user=request.user,
        initial=initial,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profil yangilandi.")
        return redirect("portal:student_profile")
    return _render(
        request,
        "portal/student/profile.html",
        {"form": form, "student": student},
    )


@student_required
def student_courses(request):
    return _render(
        request,
        "portal/student/courses.html",
        {"enrollments": learning_services.student_enrollments(request.user)},
    )


@student_required
def student_course_detail(request, course_id):
    course = learning_services.get_student_course(request.user, course_id)
    if not course:
        messages.error(request, "Bu kursga kirish huquqingiz yo‘q.")
        return redirect("portal:student_courses")
    enrollment = get_object_or_404(
        Enrollment, student=request.user, course=course, is_active=True
    )
    completed_ids = set(
        LessonProgress.objects.filter(
            student=request.user,
            lesson__module__course=course,
            is_completed=True,
        ).values_list("lesson_id", flat=True)
    )
    return _render(
        request,
        "portal/student/course_detail.html",
        {
            "course": course,
            "enrollment": enrollment,
            "completed_ids": completed_ids,
        },
    )


@student_required
def student_lesson_detail(request, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        pk=lesson_id,
        is_published=True,
        module__is_published=True,
    )
    if not learning_services.student_can_access_course(
        request.user, lesson.module.course_id
    ):
        messages.error(request, "Bu darsga kirish huquqingiz yo‘q.")
        return redirect("portal:student_courses")
    progress = LessonProgress.objects.filter(
        student=request.user, lesson=lesson
    ).first()
    return _render(
        request,
        "portal/student/lesson_detail.html",
        {"lesson": lesson, "course": lesson.module.course, "progress": progress},
    )


@student_required
@require_http_methods(["POST"])
def student_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        pk=lesson_id,
        is_published=True,
        module__is_published=True,
    )
    if not learning_services.student_can_access_course(
        request.user, lesson.module.course_id
    ):
        messages.error(request, "Bu darsga kirish huquqingiz yo‘q.")
        return redirect("portal:student_courses")
    learning_services.mark_lesson_complete(request.user, lesson)
    messages.success(request, "Dars tugallandi deb belgilandi.")
    return redirect("portal:student_lesson_detail", lesson_id=lesson.pk)


@student_required
def student_homeworks(request):
    course_ids = _course_ids(request)
    items = list(
        Homework.objects.filter(course_id__in=course_ids, is_published=True)
        .select_related("course", "lesson")
        .order_by("-created_at")
    )
    submissions = {
        s.homework_id: s
        for s in HomeworkSubmission.objects.filter(
            student=request.user, homework_id__in=[h.pk for h in items]
        )
    }
    rows = [{"homework": hw, "submission": submissions.get(hw.pk)} for hw in items]
    return _render(
        request,
        "portal/student/homeworks.html",
        {"rows": rows},
    )


@student_required
@require_http_methods(["GET", "POST"])
def student_homework_detail(request, pk):
    homework = get_object_or_404(
        Homework.objects.select_related("course"), pk=pk, is_published=True
    )
    if not learning_services.student_can_access_course(request.user, homework.course_id):
        messages.error(request, "Bu uy vazifaga kirish huquqingiz yo‘q.")
        return redirect("portal:student_homeworks")
    submission = HomeworkSubmission.objects.filter(
        homework=homework, student=request.user
    ).first()
    form = HomeworkSubmitForm(
        request.POST or None,
        request.FILES or None,
        instance=submission,
    )
    if request.method == "POST" and form.is_valid():
        learning_services.submit_or_update_homework(
            request.user,
            homework,
            form.cleaned_data.get("answer_text") or "",
            form.cleaned_data.get("attachment"),
        )
        messages.success(request, "Uy vazifa topshirildi.")
        return redirect("portal:student_homework_detail", pk=homework.pk)
    return _render(
        request,
        "portal/student/homework_detail.html",
        {"homework": homework, "form": form, "submission": submission},
    )


@student_required
def student_quizzes(request):
    course_ids = _course_ids(request)
    items = list(
        Quiz.objects.filter(course_id__in=course_ids, is_published=True)
        .select_related("course")
        .order_by("-created_at")
    )
    latest = {}
    for attempt in QuizAttempt.objects.filter(
        student=request.user, quiz_id__in=[q.pk for q in items]
    ).order_by("-started_at"):
        latest.setdefault(attempt.quiz_id, attempt)
    rows = [{"quiz": q, "attempt": latest.get(q.pk)} for q in items]
    return _render(
        request,
        "portal/student/quizzes.html",
        {"rows": rows},
    )


@student_required
@require_http_methods(["GET", "POST"])
def student_quiz_take(request, pk):
    quiz = get_object_or_404(
        Quiz.objects.select_related("course").prefetch_related(
            "questions__choices"
        ),
        pk=pk,
        is_published=True,
    )
    if not learning_services.student_can_access_course(request.user, quiz.course_id):
        messages.error(request, "Bu quizga kirish huquqingiz yo‘q.")
        return redirect("portal:student_quizzes")
    questions = list(quiz.questions.all())
    if request.method == "POST":
        answers = {
            key.replace("q_", ""): value
            for key, value in request.POST.items()
            if key.startswith("q_")
        }
        attempt = learning_services.submit_quiz_attempt(request.user, quiz, answers)
        messages.success(request, "Quiz yakunlandi.")
        return redirect("portal:student_quiz_result", attempt_id=attempt.pk)
    return _render(
        request,
        "portal/student/quiz_take.html",
        {"quiz": quiz, "questions": questions},
    )


@student_required
def student_quiz_result(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz", "quiz__course"),
        pk=attempt_id,
        student=request.user,
    )
    return _render(
        request,
        "portal/student/quiz_result.html",
        {"attempt": attempt},
    )


@student_required
def student_exams(request):
    course_ids = _course_ids(request)
    items = list(
        Exam.objects.filter(course_id__in=course_ids, is_published=True)
        .select_related("course")
        .order_by("-created_at")
    )
    latest = {}
    for attempt in ExamAttempt.objects.filter(
        student=request.user, exam_id__in=[e.pk for e in items]
    ).order_by("-started_at"):
        latest.setdefault(attempt.exam_id, attempt)
    rows = [{"exam": e, "attempt": latest.get(e.pk)} for e in items]
    return _render(
        request,
        "portal/student/exams.html",
        {"rows": rows},
    )


@student_required
@require_http_methods(["GET", "POST"])
def student_exam_take(request, pk):
    exam = get_object_or_404(
        Exam.objects.select_related("course").prefetch_related(
            "questions__choices"
        ),
        pk=pk,
        is_published=True,
    )
    if not learning_services.student_can_access_course(request.user, exam.course_id):
        messages.error(request, "Bu imtihonga kirish huquqingiz yo‘q.")
        return redirect("portal:student_exams")
    questions = list(exam.questions.all())
    if request.method == "POST":
        answers = {
            key.replace("q_", ""): value
            for key, value in request.POST.items()
            if key.startswith("q_")
        }
        attempt = learning_services.submit_exam_attempt(request.user, exam, answers)
        messages.success(request, "Imtihon yakunlandi.")
        return redirect("portal:student_exam_result", attempt_id=attempt.pk)
    return _render(
        request,
        "portal/student/exam_take.html",
        {"exam": exam, "questions": questions},
    )


@student_required
def student_exam_result(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt.objects.select_related("exam", "exam__course"),
        pk=attempt_id,
        student=request.user,
    )
    return _render(
        request,
        "portal/student/exam_result.html",
        {"attempt": attempt},
    )


@student_required
def student_results(request):
    quiz_attempts = (
        QuizAttempt.objects.filter(student=request.user)
        .select_related("quiz", "quiz__course")
        .order_by("-started_at")[:50]
    )
    exam_attempts = (
        ExamAttempt.objects.filter(student=request.user)
        .select_related("exam", "exam__course")
        .order_by("-started_at")[:50]
    )
    homework_subs = (
        HomeworkSubmission.objects.filter(student=request.user)
        .select_related("homework", "homework__course")
        .order_by("-submitted_at")[:50]
    )
    return _render(
        request,
        "portal/student/results.html",
        {
            "quiz_attempts": quiz_attempts,
            "exam_attempts": exam_attempts,
            "homework_subs": homework_subs,
        },
    )


@student_required
def student_progress(request):
    enrollments = learning_services.student_enrollments(request.user)
    return _render(
        request,
        "portal/student/progress.html",
        {"enrollments": enrollments},
    )


@student_required
def student_certificates(request):
    items = Certificate.objects.filter(
        student=request.user, is_published=True
    ).select_related("course")
    return _render(
        request,
        "portal/student/certificates.html",
        {"items": items},
    )


@student_required
def student_notifications(request):
    items = Notification.objects.filter(recipient=request.user)
    return _render(
        request,
        "portal/student/notifications.html",
        {"items": items},
    )


@student_required
@require_http_methods(["POST"])
def student_notification_read(request, pk):
    note = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if not note.is_read:
        note.is_read = True
        note.save(update_fields=["is_read"])
    return redirect("portal:student_notifications")


@student_required
@require_http_methods(["POST"])
def student_notifications_read_all(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True
    )
    messages.success(request, "Barcha bildirishnomalar o‘qilgan deb belgilandi.")
    return redirect("portal:student_notifications")
