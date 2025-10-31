# careers/forms.py
from django import forms
from .models import Application, StudentProfile, CareerOpportunity, UserProfile, StudentGrade, CourseUnit, Semester
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# -------------------------------
# Application form
# -------------------------------
class ApplicationForm(forms.ModelForm):
    message = forms.CharField(
        label="Message (optional)",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Write a short note or cover letter to the lecturer...'
        })
    )

    class Meta:
        model = Application
        fields = ['message']


# -------------------------------
# Profile form (student)
# -------------------------------
class ProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['skills', 'enrolled_subjects']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comma-separated skills, e.g. Python, SQL'}),
            'enrolled_subjects': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Comma-separated subjects, e.g. Databases, OS'})
        }


# -------------------------------
# Registration form with role selection
# -------------------------------
ROLE_CHOICES = [
    ('student', 'Student'),
    ('lecturer', 'Lecturer'),
]

class RegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Lecturer', 'Lecturer'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            role = self.cleaned_data.get('role', 'student')
            UserProfile.objects.get_or_create(user=user, defaults={'role': role})
            if role == 'student':
                StudentProfile.objects.get_or_create(user=user)
        return user


# -------------------------------
# Lecturer Opportunity form
# -------------------------------
class OpportunityForm(forms.ModelForm):
    class Meta:
        model = CareerOpportunity
        fields = ['company', 'role', 'deadline', 'link', 'field', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the opportunity'
            }),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'field': forms.TextInput(attrs={
                'placeholder': 'Comma-separated skills/subjects required (e.g., Python, SQL, Data Analysis)'
            }),
        }
        labels = {
            'field': 'Required Skills / Subjects'
        }


# -------------------------------
# Enter Grade Form (New)
# -------------------------------
class EnterGradeForm(forms.ModelForm):
    class Meta:
        model = StudentGrade
        fields = ['course_unit', 'semester', 'score']
        widgets = {
            'course_unit': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter numeric score'}),
        }

    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        if student:
            # Optionally, limit semester choices if needed
            self.fields['semester'].queryset = Semester.objects.all()
            self.fields['course_unit'].queryset = CourseUnit.objects.all()


# -------------------------------
# Optional: Student Filter Form (for Lecturer view)
# -------------------------------
class StudentFilterForm(forms.Form):
    semester = forms.ModelChoiceField(queryset=Semester.objects.all(), required=False, empty_label="All Semesters")
    student_name = forms.CharField(max_length=100, required=False, label="Student Name")
