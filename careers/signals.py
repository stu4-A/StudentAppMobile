# careers/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import StudentGrade

@receiver(post_save, sender=StudentGrade)
def notify_student_when_marks_uploaded(sender, instance, created, **kwargs):
    """
    Sends an email to the student when marks are uploaded by a lecturer.
    """
    if created:  # only trigger on new record creation
        student_user = instance.student.user
        student_email = student_user.email

        if not student_email:
            return  # no email, skip sending

        lecturer_name = (
            instance.lecturer.get_full_name() if instance.lecturer else "Your Lecturer"
        )
        course_name = instance.course_unit
        score = instance.score
        grade = instance.grade

        subject = f"Marks Uploaded for {course_name}"
        message = (
            f"Dear {student_user.first_name or student_user.username},\n\n"
            f"{lecturer_name} has uploaded your marks for {course_name}.\n"
            f"Score: {score}\n"
            f"Grade: {grade}\n\n"
            f"Kind regards,\n"
            f"University Academic Portal"
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [student_email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")
