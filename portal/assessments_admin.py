import secrets

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.permissions import admin_required
from learning.forms import (
    CertificateForm,
    ExamChoiceFormSet,
    ExamForm,
    ExamQuestionForm,
    HomeworkForm,
    NotificationForm,
    QuizChoiceFormSet,
    QuizForm,
    QuizQuestionForm,
)
from learning.models import (
    Certificate,
    Exam,
    ExamQuestion,
    Homework,
    Notification,
    Quiz,
    QuizQuestion,
)


def _render(request, template, context=None):
    return render(request, template, context or {})


def _new_certificate_code() -> str:
    return secrets.token_hex(8).upper()


# ---- Homework ----


@admin_required
def admin_homeworks(request):
    return _render(
        request,
        "portal/admin/homeworks.html",
        {
            "items": Homework.objects.select_related("course", "lesson").all(),
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_homework_create(request):
    form = HomeworkForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Uy vazifa yaratildi.")
        return redirect("portal:admin_homeworks")
    return _render(
        request,
        "portal/admin/homework_form.html",
        {"form": form, "title": "Yangi uy vazifa"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_homework_edit(request, pk):
    obj = get_object_or_404(Homework, pk=pk)
    form = HomeworkForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Uy vazifa yangilandi.")
        return redirect("portal:admin_homeworks")
    return _render(
        request,
        "portal/admin/homework_form.html",
        {"form": form, "title": "Uy vazifa tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_homework_delete(request, pk):
    get_object_or_404(Homework, pk=pk).delete()
    messages.success(request, "Uy vazifa o‘chirildi.")
    return redirect("portal:admin_homeworks")


# ---- Quiz ----


@admin_required
def admin_quizzes(request):
    return _render(
        request,
        "portal/admin/quizzes.html",
        {"items": Quiz.objects.select_related("course", "module").all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_quiz_create(request):
    form = QuizForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        quiz = form.save()
        messages.success(request, "Quiz yaratildi.")
        return redirect("portal:admin_quiz_questions", quiz_id=quiz.pk)
    return _render(
        request,
        "portal/admin/quiz_form.html",
        {"form": form, "title": "Yangi quiz"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_quiz_edit(request, pk):
    obj = get_object_or_404(Quiz, pk=pk)
    form = QuizForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Quiz yangilandi.")
        return redirect("portal:admin_quizzes")
    return _render(
        request,
        "portal/admin/quiz_form.html",
        {"form": form, "title": "Quiz tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_quiz_delete(request, pk):
    get_object_or_404(Quiz, pk=pk).delete()
    messages.success(request, "Quiz o‘chirildi.")
    return redirect("portal:admin_quizzes")


@admin_required
def admin_quiz_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz.objects.select_related("course"), pk=quiz_id)
    return _render(
        request,
        "portal/admin/quiz_questions.html",
        {"quiz": quiz, "items": quiz.questions.prefetch_related("choices").all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_quiz_question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    form = QuizQuestionForm(request.POST or None)
    formset = QuizChoiceFormSet(request.POST or None)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            formset.instance = question
            formset.save()
        messages.success(request, "Savol qo‘shildi.")
        return redirect("portal:admin_quiz_questions", quiz_id=quiz.pk)
    return _render(
        request,
        "portal/admin/quiz_question_form.html",
        {
            "form": form,
            "formset": formset,
            "quiz": quiz,
            "title": "Yangi savol",
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_quiz_question_edit(request, pk):
    obj = get_object_or_404(QuizQuestion.objects.select_related("quiz"), pk=pk)
    form = QuizQuestionForm(request.POST or None, instance=obj)
    formset = QuizChoiceFormSet(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            form.save()
            formset.save()
        messages.success(request, "Savol yangilandi.")
        return redirect("portal:admin_quiz_questions", quiz_id=obj.quiz_id)
    return _render(
        request,
        "portal/admin/quiz_question_form.html",
        {
            "form": form,
            "formset": formset,
            "quiz": obj.quiz,
            "title": "Savol tahrirlash",
            "obj": obj,
        },
    )


@admin_required
@require_http_methods(["POST"])
def admin_quiz_question_delete(request, pk):
    obj = get_object_or_404(QuizQuestion, pk=pk)
    quiz_id = obj.quiz_id
    obj.delete()
    messages.success(request, "Savol o‘chirildi.")
    return redirect("portal:admin_quiz_questions", quiz_id=quiz_id)


# ---- Exam ----


@admin_required
def admin_exams(request):
    return _render(
        request,
        "portal/admin/exams.html",
        {"items": Exam.objects.select_related("course").all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_exam_create(request):
    form = ExamForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        exam = form.save()
        messages.success(request, "Imtihon yaratildi.")
        return redirect("portal:admin_exam_questions", exam_id=exam.pk)
    return _render(
        request,
        "portal/admin/exam_form.html",
        {"form": form, "title": "Yangi imtihon"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_exam_edit(request, pk):
    obj = get_object_or_404(Exam, pk=pk)
    form = ExamForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Imtihon yangilandi.")
        return redirect("portal:admin_exams")
    return _render(
        request,
        "portal/admin/exam_form.html",
        {"form": form, "title": "Imtihon tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_exam_delete(request, pk):
    get_object_or_404(Exam, pk=pk).delete()
    messages.success(request, "Imtihon o‘chirildi.")
    return redirect("portal:admin_exams")


@admin_required
def admin_exam_questions(request, exam_id):
    exam = get_object_or_404(Exam.objects.select_related("course"), pk=exam_id)
    return _render(
        request,
        "portal/admin/exam_questions.html",
        {"exam": exam, "items": exam.questions.prefetch_related("choices").all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_exam_question_create(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    form = ExamQuestionForm(request.POST or None)
    formset = ExamChoiceFormSet(request.POST or None)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            formset.instance = question
            formset.save()
        messages.success(request, "Savol qo‘shildi.")
        return redirect("portal:admin_exam_questions", exam_id=exam.pk)
    return _render(
        request,
        "portal/admin/exam_question_form.html",
        {
            "form": form,
            "formset": formset,
            "exam": exam,
            "title": "Yangi savol",
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_exam_question_edit(request, pk):
    obj = get_object_or_404(ExamQuestion.objects.select_related("exam"), pk=pk)
    form = ExamQuestionForm(request.POST or None, instance=obj)
    formset = ExamChoiceFormSet(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            form.save()
            formset.save()
        messages.success(request, "Savol yangilandi.")
        return redirect("portal:admin_exam_questions", exam_id=obj.exam_id)
    return _render(
        request,
        "portal/admin/exam_question_form.html",
        {
            "form": form,
            "formset": formset,
            "exam": obj.exam,
            "title": "Savol tahrirlash",
            "obj": obj,
        },
    )


@admin_required
@require_http_methods(["POST"])
def admin_exam_question_delete(request, pk):
    obj = get_object_or_404(ExamQuestion, pk=pk)
    exam_id = obj.exam_id
    obj.delete()
    messages.success(request, "Savol o‘chirildi.")
    return redirect("portal:admin_exam_questions", exam_id=exam_id)


# ---- Certificates ----


@admin_required
def admin_certificates(request):
    return _render(
        request,
        "portal/admin/certificates.html",
        {
            "items": Certificate.objects.select_related(
                "student", "student__profile", "course"
            ).all()
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_certificate_create(request):
    form = CertificateForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        cert = form.save(commit=False)
        if not (cert.certificate_code or "").strip():
            cert.certificate_code = _new_certificate_code()
        cert.save()
        messages.success(request, "Sertifikat yaratildi.")
        return redirect("portal:admin_certificates")
    return _render(
        request,
        "portal/admin/certificate_form.html",
        {"form": form, "title": "Yangi sertifikat"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_certificate_edit(request, pk):
    obj = get_object_or_404(Certificate, pk=pk)
    form = CertificateForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        cert = form.save(commit=False)
        if not (cert.certificate_code or "").strip():
            cert.certificate_code = _new_certificate_code()
        cert.save()
        messages.success(request, "Sertifikat yangilandi.")
        return redirect("portal:admin_certificates")
    return _render(
        request,
        "portal/admin/certificate_form.html",
        {"form": form, "title": "Sertifikat tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_certificate_delete(request, pk):
    get_object_or_404(Certificate, pk=pk).delete()
    messages.success(request, "Sertifikat o‘chirildi.")
    return redirect("portal:admin_certificates")


# ---- Notifications ----


@admin_required
def admin_notifications(request):
    return _render(
        request,
        "portal/admin/notifications.html",
        {
            "items": Notification.objects.select_related(
                "recipient", "recipient__profile"
            ).all()[:200]
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_notification_create(request):
    form = NotificationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Bildirishnoma yuborildi.")
        return redirect("portal:admin_notifications")
    return _render(
        request,
        "portal/admin/notification_form.html",
        {"form": form, "title": "Yangi bildirishnoma"},
    )


@admin_required
@require_http_methods(["POST"])
def admin_notification_delete(request, pk):
    get_object_or_404(Notification, pk=pk).delete()
    messages.success(request, "Bildirishnoma o‘chirildi.")
    return redirect("portal:admin_notifications")
