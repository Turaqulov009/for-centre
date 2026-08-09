from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.forms import inlineformset_factory
from django.utils.text import slugify

from accounts.models import Role
from learning.models import (
    Certificate,
    Course,
    Enrollment,
    Exam,
    ExamChoice,
    ExamQuestion,
    Homework,
    Lesson,
    Module,
    Notification,
    Quiz,
    QuizChoice,
    QuizQuestion,
    Subject,
    Teacher,
)

User = get_user_model()


def _unique_course_slug(title: str, instance=None) -> str:
    base = slugify(title) or "course"
    slug = base
    n = 2
    qs = Course.objects.filter(slug=slug)
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.exists():
        slug = f"{base}-{n}"
        n += 1
        qs = Course.objects.filter(slug=slug)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
    return slug


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["title", "description", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            "full_name",
            "specialty",
            "bio",
            "photo",
            "phone",
            "email",
            "user",
            "is_active",
            "show_on_landing",
            "sort_order",
        ]
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = User.objects.filter(profile__role=Role.TEACHER, is_active=True)
        if self.instance and self.instance.user_id:
            qs = User.objects.filter(
                Q(pk=self.instance.user_id) | Q(profile__role=Role.TEACHER, is_active=True)
            )
        self.fields["user"].queryset = qs.order_by("username")
        self.fields["user"].required = False
        self.fields["user"].label = "Bog‘langan user (Teacher)"


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "slug",
            "short_description",
            "description",
            "cover",
            "subject",
            "teacher",
            "duration",
            "is_published",
            "show_on_landing",
            "sort_order",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "slug": forms.TextInput(attrs={"placeholder": "Bo‘sh qoldirilsa avtomatik"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        subjects = Subject.objects.filter(is_active=True)
        teachers = Teacher.objects.filter(is_active=True)
        if self.instance and self.instance.subject_id:
            subjects = Subject.objects.filter(
                Q(pk=self.instance.subject_id) | Q(is_active=True)
            )
        if self.instance and self.instance.teacher_id:
            teachers = Teacher.objects.filter(
                Q(pk=self.instance.teacher_id) | Q(is_active=True)
            )
        self.fields["subject"].queryset = subjects.order_by("title")
        self.fields["teacher"].queryset = teachers.order_by("full_name")

    def clean(self):
        cleaned = super().clean()
        slug = (cleaned.get("slug") or "").strip()
        title = (cleaned.get("title") or "").strip()
        if not slug:
            slug = _unique_course_slug(title, self.instance)
        else:
            qs = Course.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                slug = _unique_course_slug(slug, self.instance)
        cleaned["slug"] = slug
        return cleaned


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ["title", "description", "sort_order", "is_published"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            "title",
            "content",
            "video_url",
            "duration_minutes",
            "sort_order",
            "is_published",
        ]
        widgets = {"content": forms.Textarea(attrs={"rows": 6})}


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "course", "is_active", "progress_percent"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        students = User.objects.filter(profile__role=Role.STUDENT, is_active=True)
        if self.instance and self.instance.student_id:
            students = User.objects.filter(
                Q(pk=self.instance.student_id)
                | Q(profile__role=Role.STUDENT, is_active=True)
            )
        self.fields["student"].queryset = students.order_by("username")
        self.fields["course"].queryset = Course.objects.all().order_by("title")
        self.fields["student"].label = "Student"
        self.fields["progress_percent"].widget.attrs["min"] = 0
        self.fields["progress_percent"].widget.attrs["max"] = 100


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = [
            "course",
            "lesson",
            "title",
            "description",
            "due_date",
            "is_published",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"type": "datetime-local"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.all().order_by("title")
        self.fields["lesson"].queryset = Lesson.objects.select_related(
            "module__course"
        ).order_by("module__course__title", "sort_order")
        self.fields["lesson"].required = False
        self.fields["lesson"].label = "Dars (ixtiyoriy)"
        self.fields["due_date"].required = False
        self.fields["due_date"].input_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = [
            "course",
            "module",
            "title",
            "description",
            "time_limit_minutes",
            "is_published",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.all().order_by("title")
        self.fields["module"].queryset = Module.objects.select_related("course").order_by(
            "course__title", "sort_order"
        )
        self.fields["module"].required = False


class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ["text", "sort_order", "points"]
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}


QuizChoiceFormSet = inlineformset_factory(
    QuizQuestion,
    QuizChoice,
    fields=["text", "is_correct"],
    extra=4,
    can_delete=True,
)


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            "course",
            "title",
            "description",
            "time_limit_minutes",
            "is_published",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.all().order_by("title")


class ExamQuestionForm(forms.ModelForm):
    class Meta:
        model = ExamQuestion
        fields = ["text", "sort_order", "points"]
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}


ExamChoiceFormSet = inlineformset_factory(
    ExamQuestion,
    ExamChoice,
    fields=["text", "is_correct"],
    extra=4,
    can_delete=True,
)


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = [
            "student",
            "course",
            "title",
            "certificate_code",
            "file",
            "is_published",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        students = User.objects.filter(profile__role=Role.STUDENT, is_active=True)
        if self.instance and self.instance.student_id:
            students = User.objects.filter(
                Q(pk=self.instance.student_id)
                | Q(profile__role=Role.STUDENT, is_active=True)
            )
        self.fields["student"].queryset = students.order_by("username")
        self.fields["course"].queryset = Course.objects.all().order_by("title")
        self.fields["certificate_code"].required = False
        self.fields["certificate_code"].help_text = (
            "Bo‘sh qoldirilsa avtomatik yaratiladi."
        )
        self.fields["file"].required = False


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ["recipient", "title", "message", "link"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["recipient"].queryset = User.objects.filter(is_active=True).order_by(
            "username"
        )
        self.fields["link"].required = False
        self.fields["link"].help_text = "Ixtiyoriy ichki yoki tashqi URL"
