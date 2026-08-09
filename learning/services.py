from django.db.models import Prefetch
from django.utils import timezone

from accounts.models import Role, StudentProfile
from learning.models import (
    Certificate,
    Course,
    Enrollment,
    Exam,
    ExamAttempt,
    Homework,
    HomeworkSubmission,
    Lesson,
    LessonProgress,
    Module,
    Notification,
    Quiz,
    QuizAttempt,
    Teacher,
)


def platform_statistics() -> dict:
    """Landing/admin statistikalar — faqat database hisobi."""
    return {
        "students_count": StudentProfile.objects.filter(
            user__profile__role=Role.STUDENT,
            user__is_active=True,
        ).count(),
        "graduates_count": StudentProfile.objects.filter(
            is_graduated=True,
            user__is_active=True,
        ).count(),
        "courses_count": Course.objects.filter(is_published=True).count(),
        "teachers_count": Teacher.objects.filter(is_active=True).count(),
        "published_courses_total": Course.objects.count(),
    }


def student_enrollments(user):
    return (
        Enrollment.objects.filter(student=user, is_active=True)
        .select_related("course", "course__teacher", "course__subject")
        .order_by("-enrolled_at")
    )


def student_course_ids(user):
    return list(
        Enrollment.objects.filter(student=user, is_active=True).values_list(
            "course_id", flat=True
        )
    )


def student_can_access_course(user, course_id: int) -> bool:
    return Enrollment.objects.filter(
        student=user, course_id=course_id, is_active=True
    ).exists()


def get_student_course(user, course_id: int) -> Course | None:
    if not student_can_access_course(user, course_id):
        return None
    return (
        Course.objects.filter(pk=course_id)
        .prefetch_related(
            Prefetch(
                "modules",
                queryset=Module.objects.filter(is_published=True)
                .prefetch_related(
                    Prefetch(
                        "lessons",
                        queryset=Lesson.objects.filter(is_published=True),
                    )
                )
                .order_by("sort_order", "id"),
            )
        )
        .select_related("teacher", "subject")
        .first()
    )


def recalculate_course_progress(user, course) -> int:
    lesson_ids = list(
        Lesson.objects.filter(
            module__course=course, module__is_published=True, is_published=True
        ).values_list("id", flat=True)
    )
    total = len(lesson_ids)
    if total == 0:
        percent = 0
    else:
        done = LessonProgress.objects.filter(
            student=user, lesson_id__in=lesson_ids, is_completed=True
        ).count()
        percent = int(round(done * 100 / total))
    Enrollment.objects.filter(student=user, course=course).update(
        progress_percent=percent
    )
    return percent


def mark_lesson_complete(user, lesson: Lesson) -> LessonProgress:
    progress, _ = LessonProgress.objects.get_or_create(
        student=user, lesson=lesson, defaults={"is_completed": False}
    )
    if not progress.is_completed:
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save(update_fields=["is_completed", "completed_at"])
    recalculate_course_progress(user, lesson.module.course)
    return progress


def grade_choice_answers(questions, answers: dict) -> tuple:
    score = 0
    max_score = 0
    for question in questions:
        max_score += question.points
        raw = answers.get(str(question.pk)) or answers.get(question.pk)
        if not raw:
            continue
        try:
            choice_id = int(raw)
        except (TypeError, ValueError):
            continue
        if question.choices.filter(pk=choice_id, is_correct=True).exists():
            score += question.points
    return score, max_score


def submit_quiz_attempt(user, quiz: Quiz, answers: dict) -> QuizAttempt:
    questions = list(quiz.questions.prefetch_related("choices").all())
    score, max_score = grade_choice_answers(questions, answers)
    return QuizAttempt.objects.create(
        quiz=quiz,
        student=user,
        score=score,
        max_score=max_score,
        finished_at=timezone.now(),
    )


def submit_exam_attempt(user, exam: Exam, answers: dict) -> ExamAttempt:
    questions = list(exam.questions.prefetch_related("choices").all())
    score, max_score = grade_choice_answers(questions, answers)
    return ExamAttempt.objects.create(
        exam=exam,
        student=user,
        score=score,
        max_score=max_score,
        finished_at=timezone.now(),
    )


def avg_progress(user) -> int:
    rows = list(
        Enrollment.objects.filter(student=user, is_active=True).values_list(
            "progress_percent", flat=True
        )
    )
    if not rows:
        return 0
    return int(round(sum(rows) / len(rows)))


def student_dashboard_stats(user) -> dict:
    course_ids = student_course_ids(user)
    unread = Notification.objects.filter(recipient=user, is_read=False).count()
    return {
        "courses_count": len(course_ids),
        "homeworks_count": Homework.objects.filter(
            course_id__in=course_ids, is_published=True
        ).count(),
        "quizzes_count": Quiz.objects.filter(
            course_id__in=course_ids, is_published=True
        ).count(),
        "exams_count": Exam.objects.filter(
            course_id__in=course_ids, is_published=True
        ).count(),
        "certificates_count": Certificate.objects.filter(
            student=user, is_published=True
        ).count(),
        "unread_notifications": unread,
        "avg_progress": avg_progress(user),
    }


def _avg_progress(user) -> int:
    return avg_progress(user)

def submit_or_update_homework(user, homework: Homework, answer_text: str, attachment):
    submission, created = HomeworkSubmission.objects.get_or_create(
        homework=homework,
        student=user,
        defaults={
            "answer_text": answer_text,
            "attachment": attachment,
            "status": HomeworkSubmission.Status.SUBMITTED,
        },
    )
    if not created:
        submission.answer_text = answer_text
        if attachment:
            submission.attachment = attachment
        submission.status = HomeworkSubmission.Status.SUBMITTED
        submission.save()
    return submission
