from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# -------------------------------
# User Profile for Role-Based Access
# -------------------------------
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# -------------------------------
# Student Profile
# -------------------------------
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentprofile')
    skills = models.TextField(blank=True, help_text='Comma-separated skills like Python,SQL')
    enrolled_subjects = models.TextField(blank=True, help_text='Comma-separated subject names')
    cgpa = models.FloatField(default=0.0, help_text='Cumulative GPA across all semesters')
    gpa = models.FloatField(default=0)
   


    def __str__(self):
        return self.user.get_full_name() or self.user.username

# -------------------------------
# Career Opportunity
# -------------------------------
class CareerOpportunity(models.Model):
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=300)
    deadline = models.DateField()
    link = models.URLField(blank=True)
    # Change field to TextField to allow multiple comma-separated subjects/skills
    field = models.TextField(blank=True, help_text='Comma-separated required subjects/skills')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='posted_opportunities')

    def __str__(self):
        return f"{self.company} - {self.role}"


# -------------------------------
# Saved Opportunity (Student)
# -------------------------------
class SavedOpportunity(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='saved_opportunities')
    opportunity = models.ForeignKey(CareerOpportunity, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'opportunity')

    def __str__(self):
        return f"{self.student} saved {self.opportunity}"

# -------------------------------
# Application (Student)
# -------------------------------
class Application(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    opportunity = models.ForeignKey(CareerOpportunity, on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'opportunity')

    def __str__(self):
        return f"{self.student} -> {self.opportunity}"

# -------------------------------
# Notification (Student)
# -------------------------------
class Notification(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.student}: {self.message[:40]}"

# -------------------------------
# Student Grade (for GPA/CGPA)
# -------------------------------
# -------------------------------
# Student Grade (for GPA/CGPA)
# -------------------------------
class Semester(models.Model):
    SEMESTER_CHOICES = [
        ('1', 'First Semester'),
        ('2', 'Second Semester'),
        ('3', 'Third Semester'),
    ]
    year = models.CharField(max_length=9)  # Example: "2025/2026"
    name = models.CharField(max_length=10, choices=SEMESTER_CHOICES)

    class Meta:
        unique_together = ('year', 'name')

    def __str__(self):
        return f"{self.year} - {self.get_name_display()}"


class CourseUnit(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    credit_units = models.PositiveIntegerField(default=3)

    def __str__(self):
        return f"{self.code} - {self.name}"


from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class StudentGrade(models.Model):
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='grades'
    )

    lecturer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_grades'
    )

    course_unit = models.CharField(max_length=100)
    semester = models.ForeignKey(
        'Semester',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    score = models.FloatField(default=0.0, help_text='Numeric score, e.g. 85.0')
    recorded_at = models.DateTimeField(auto_now_add=True)
    opportunity = models.ForeignKey(
        'CareerOpportunity',
        on_delete=models.CASCADE,
        related_name='grades',
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('student', 'course_unit', 'semester')

    # Default credit units
    @property
    def credit_units(self):
        return 3  # Default per course

    # Letter grade matching JS template
    @property
    def grade(self):
        if self.score >= 80:
            return 'A'
        elif self.score >= 75:
            return 'B+'
        elif self.score >= 70:
            return 'B'
        elif self.score >= 65:
            return 'C+'
        elif self.score >= 60:
            return 'C'
        elif self.score >= 50:
            return 'D'
        else:
            return 'F'

    # Grade points matching JS template
    @property
    def grade_points(self):
        mapping = {
            'A': 5.0,
            'B+': 4.5,
            'B': 4.0,
            'C+': 3.5,
            'C': 3.0,
            'D': 2.0,
            'F': 0.0
        }
        return mapping.get(self.grade, 0.0) * self.credit_units

    # GPA for single semester
    @staticmethod
    def calculate_gpa(student, semester):
        grades = StudentGrade.objects.filter(student=student, semester=semester)
        total_points = sum(g.grade_points for g in grades)
        total_credits = sum(g.credit_units for g in grades)
        return round(total_points / total_credits, 2) if total_credits else 0.0

    # Cumulative GPA across all semesters
    @staticmethod
    def calculate_cgpa(student):
        grades = StudentGrade.objects.filter(student=student)
        total_points = sum(g.grade_points for g in grades)
        total_credits = sum(g.credit_units for g in grades)
        return round(total_points / total_credits, 2) if total_credits else 0.0



# -------------------------------
# Signals to ensure profiles exist
# -------------------------------
@receiver(post_save, sender=User)
def ensure_profiles(sender, instance, created, **kwargs):
    if created:
        # New user: create UserProfile and StudentProfile
        UserProfile.objects.create(user=instance, role='student')
        StudentProfile.objects.get_or_create(user=instance)
    else:
        # Existing user: ensure profiles exist
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(user=instance, role='student')
        if hasattr(instance, 'userprofile') and instance.userprofile.role == 'student':
            if not hasattr(instance, 'studentprofile'):
                StudentProfile.objects.create(user=instance)




from django.contrib.auth.models import User

# careers/models.py
from django.db import models
from django.contrib.auth.models import User

class GeneratedReport(models.Model):
    file = models.FileField(upload_to='reports/')
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ready', 'Ready'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.file.name} ({self.status})"
