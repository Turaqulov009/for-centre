from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.permissions import admin_required
from learning.forms import (
    CourseForm,
    EnrollmentForm,
    LessonForm,
    ModuleForm,
    SubjectForm,
    TeacherForm,
)
from learning.models import Course, Enrollment, Lesson, Module, Subject, Teacher


def _render(request, template, context=None):
    return render(request, template, context or {})


# ---- Subjects ----


@admin_required
def admin_subjects(request):
    return _render(request, "portal/admin/subjects.html", {"items": Subject.objects.all()})


@admin_required
@require_http_methods(["GET", "POST"])
def admin_subject_create(request):
    form = SubjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Fan yaratildi.")
        return redirect("portal:admin_subjects")
    return _render(
        request,
        "portal/admin/subject_form.html",
        {"form": form, "title": "Yangi fan"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_subject_edit(request, pk):
    obj = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Fan yangilandi.")
        return redirect("portal:admin_subjects")
    return _render(
        request,
        "portal/admin/subject_form.html",
        {"form": form, "title": "Fan tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_subject_delete(request, pk):
    get_object_or_404(Subject, pk=pk).delete()
    messages.success(request, "Fan o‘chirildi.")
    return redirect("portal:admin_subjects")


# ---- Teachers ----


@admin_required
def admin_teachers(request):
    return _render(request, "portal/admin/teachers.html", {"items": Teacher.objects.all()})


@admin_required
@require_http_methods(["GET", "POST"])
def admin_teacher_create(request):
    form = TeacherForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "O‘qituvchi yaratildi.")
        return redirect("portal:admin_teachers")
    return _render(
        request,
        "portal/admin/teacher_form.html",
        {"form": form, "title": "Yangi o‘qituvchi"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_teacher_edit(request, pk):
    obj = get_object_or_404(Teacher, pk=pk)
    form = TeacherForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "O‘qituvchi yangilandi.")
        return redirect("portal:admin_teachers")
    return _render(
        request,
        "portal/admin/teacher_form.html",
        {"form": form, "title": "O‘qituvchi tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_teacher_delete(request, pk):
    get_object_or_404(Teacher, pk=pk).delete()
    messages.success(request, "O‘qituvchi o‘chirildi.")
    return redirect("portal:admin_teachers")


# ---- Courses ----


@admin_required
def admin_courses(request):
    return _render(
        request,
        "portal/admin/courses.html",
        {"items": Course.objects.select_related("subject", "teacher").all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_course_create(request):
    form = CourseForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kurs yaratildi.")
        return redirect("portal:admin_courses")
    return _render(
        request,
        "portal/admin/course_form.html",
        {"form": form, "title": "Yangi kurs"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_course_edit(request, pk):
    obj = get_object_or_404(Course, pk=pk)
    form = CourseForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kurs yangilandi.")
        return redirect("portal:admin_courses")
    return _render(
        request,
        "portal/admin/course_form.html",
        {"form": form, "title": "Kurs tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_course_delete(request, pk):
    get_object_or_404(Course, pk=pk).delete()
    messages.success(request, "Kurs o‘chirildi.")
    return redirect("portal:admin_courses")


# ---- Modules (nested under course) ----


@admin_required
def admin_course_modules(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return _render(
        request,
        "portal/admin/modules.html",
        {"course": course, "items": course.modules.all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_module_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    form = ModuleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        module = form.save(commit=False)
        module.course = course
        module.save()
        messages.success(request, "Modul yaratildi.")
        return redirect("portal:admin_course_modules", course_id=course.pk)
    return _render(
        request,
        "portal/admin/module_form.html",
        {"form": form, "title": "Yangi modul", "course": course},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_module_edit(request, pk):
    obj = get_object_or_404(Module.objects.select_related("course"), pk=pk)
    form = ModuleForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Modul yangilandi.")
        return redirect("portal:admin_course_modules", course_id=obj.course_id)
    return _render(
        request,
        "portal/admin/module_form.html",
        {"form": form, "title": "Modul tahrirlash", "course": obj.course, "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_module_delete(request, pk):
    obj = get_object_or_404(Module, pk=pk)
    course_id = obj.course_id
    obj.delete()
    messages.success(request, "Modul o‘chirildi.")
    return redirect("portal:admin_course_modules", course_id=course_id)


# ---- Lessons (nested under module) ----


@admin_required
def admin_module_lessons(request, module_id):
    module = get_object_or_404(Module.objects.select_related("course"), pk=module_id)
    return _render(
        request,
        "portal/admin/lessons.html",
        {"module": module, "course": module.course, "items": module.lessons.all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_lesson_create(request, module_id):
    module = get_object_or_404(Module.objects.select_related("course"), pk=module_id)
    form = LessonForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        lesson = form.save(commit=False)
        lesson.module = module
        lesson.save()
        messages.success(request, "Dars yaratildi.")
        return redirect("portal:admin_module_lessons", module_id=module.pk)
    return _render(
        request,
        "portal/admin/lesson_form.html",
        {
            "form": form,
            "title": "Yangi dars",
            "module": module,
            "course": module.course,
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_lesson_edit(request, pk):
    obj = get_object_or_404(Lesson.objects.select_related("module__course"), pk=pk)
    form = LessonForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Dars yangilandi.")
        return redirect("portal:admin_module_lessons", module_id=obj.module_id)
    return _render(
        request,
        "portal/admin/lesson_form.html",
        {
            "form": form,
            "title": "Dars tahrirlash",
            "module": obj.module,
            "course": obj.module.course,
            "obj": obj,
        },
    )


@admin_required
@require_http_methods(["POST"])
def admin_lesson_delete(request, pk):
    obj = get_object_or_404(Lesson, pk=pk)
    module_id = obj.module_id
    obj.delete()
    messages.success(request, "Dars o‘chirildi.")
    return redirect("portal:admin_module_lessons", module_id=module_id)


# ---- Enrollments ----


@admin_required
def admin_enrollments(request):
    return _render(
        request,
        "portal/admin/enrollments.html",
        {
            "items": Enrollment.objects.select_related(
                "student", "student__profile", "course"
            ).all()
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_enrollment_create(request):
    form = EnrollmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student kursga biriktirildi.")
        return redirect("portal:admin_enrollments")
    return _render(
        request,
        "portal/admin/enrollment_form.html",
        {"form": form, "title": "Yangi enrollment"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_enrollment_edit(request, pk):
    obj = get_object_or_404(Enrollment, pk=pk)
    form = EnrollmentForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Enrollment yangilandi.")
        return redirect("portal:admin_enrollments")
    return _render(
        request,
        "portal/admin/enrollment_form.html",
        {"form": form, "title": "Enrollment tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_enrollment_delete(request, pk):
    get_object_or_404(Enrollment, pk=pk).delete()
    messages.success(request, "Enrollment o‘chirildi.")
    return redirect("portal:admin_enrollments")
