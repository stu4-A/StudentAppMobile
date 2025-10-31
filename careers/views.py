import io
import csv
import zipfile
import tempfile
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple

from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image as RLImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import csv
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


import threading
import csv
import os
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from .models import CareerOpportunity, GeneratedReport
from django.contrib.auth.decorators import login_required, user_passes_test


from .models import (
    CareerOpportunity, StudentProfile, SavedOpportunity, Application,
    Notification, UserProfile, StudentGrade
)
from .forms import ApplicationForm, ProfileForm, RegistrationForm, OpportunityForm
from .decorators import student_required, lecturer_required
from .utils.grades import compute_gpa_summary


# -------------------------------
# Custom Login View
# -------------------------------
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user

        # Admin/superuser goes to admin dashboard
        if user.is_staff or user.is_superuser:
            return '/careers/admin-dashboard/'

        # Check role-based redirects
        try:
            profile = user.userprofile
            if profile.role == 'lecturer':
                return '/careers/manage/'  # lecturer dashboard
            elif profile.role == 'student':
                return '/careers/list/'  # student dashboard or homepage
        except (AttributeError, UserProfile.DoesNotExist):
            pass

        # Fallback
        return '/'
    




def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Add context if needed
    return render(request, 'careers/admin_dashboard.html')
# -------------------------------
# Home Page
# -------------------------------
def home(request):
    is_student = False
    is_lecturer = False
    if request.user.is_authenticated:
        is_student = request.user.groups.filter(name='Student').exists()
        is_lecturer = request.user.groups.filter(name='Lecturer').exists()
    context = {
        'is_student': is_student,
        'is_lecturer': is_lecturer,
    }
    return render(request, 'careers/home.html', context)



# -------------------------------
# Helper: get StudentProfile for logged-in student
# -------------------------------
def get_student_profile_for_request(request):
    if not request.user.is_authenticated:
        return None
    try:
        profile = request.user.userprofile
        if profile.role != 'student':
            return None
        sp, _ = StudentProfile.objects.get_or_create(user=request.user)
        return sp
    except UserProfile.DoesNotExist:
        return None

# -------------------------------
# Student: Opportunity List
# -------------------------------
# careers/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import CareerOpportunity, StudentGrade
from .utils.grades import compute_gpa_summary
from .utils.matching import recommend_opportunities
from .decorators import student_required
from .helpers import get_student_profile_for_request


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from careers.models import CareerOpportunity, StudentProfile, StudentGrade, Semester
from careers.utils.grades import compute_gpa_summary
#from careers.recommendations import recommend_opportunities

@login_required
@student_required
def opportunity_list(request):
    from django.db.models import Q

    # ---------------------------
    # 1. Career Opportunities Query & Filter
    # ---------------------------
    qs = CareerOpportunity.objects.all()
    q = request.GET.get('q', '').strip()
    filt = request.GET.get('filter', '').strip()

    if q:
        qs = qs.filter(
            Q(company__icontains=q) |
            Q(role__icontains=q) |
            Q(description__icontains=q)
        )

    if filt == 'deadline':
        qs = qs.order_by('deadline')
    elif filt == 'newest':
        qs = qs.order_by('-created_at')
    else:
        qs = qs.order_by('deadline')

    opportunities = qs[:200]

    # ---------------------------
    # 2. Student Profile & GPA/CGPA
    # ---------------------------
    sp = get_student_profile_for_request(request)
    student_gpa = student_cgpa = 0.0
    grades_by_semester = {}

    if sp:
        grades_qs = StudentGrade.objects.filter(student=sp).select_related('semester')
        # Compute GPA per current semester
        current_semester = Semester.objects.order_by('-year', '-name').first()
        if current_semester:
            student_gpa = StudentGrade.calculate_gpa(sp, current_semester)
        # Compute CGPA across all semesters
        student_cgpa = StudentGrade.calculate_cgpa(sp)

        # Organize grades per semester
        semesters = Semester.objects.all().order_by('-year', 'name')
        for sem in semesters:
            sem_grades = grades_qs.filter(semester=sem)
            if sem_grades.exists():
                grades_by_semester[sem] = sem_grades

    # ---------------------------
    # 3. Smart Recommendations
    # ---------------------------
    recommendations = recommend_opportunities(sp, opportunities)[:5] if sp else []

    # ---------------------------
    # 4. Context
    # ---------------------------
    context = {
        'opportunities': opportunities,
        'q': q,
        'filter': filt,
        'recommendations': recommendations,
        'student_gpa': student_gpa,
        'student_cgpa': student_cgpa,
        'grades_by_semester': grades_by_semester,
        'quick_tips': [
            "Update your profile regularly.",
            "Apply early for opportunities.",
            "Check notifications daily.",
            "Focus on internships matching your skills.",
        ],
    }

    return render(request, 'careers/opportunity_list.html', context)



# -------------------------------
# Opportunity Detail
# -------------------------------
@login_required
@student_required
def opportunity_detail(request, pk):
    opp = get_object_or_404(CareerOpportunity, pk=pk)
    sp = get_student_profile_for_request(request)
    saved = SavedOpportunity.objects.filter(student=sp, opportunity=opp).exists() if sp else False
    applied = Application.objects.filter(student=sp, opportunity=opp).exists() if sp else False
    form = ApplicationForm()
    return render(request, 'careers/opportunity_detail.html', {
        'opp': opp,
        'saved': saved,
        'applied': applied,
        'form': form
    })

# -------------------------------
# Save / Unsave
# -------------------------------
@login_required
@student_required
@require_POST
def save_toggle(request, pk):
    opp = get_object_or_404(CareerOpportunity, pk=pk)
    sp = get_student_profile_for_request(request)
    if not sp:
        messages.error(request, 'Student profile not found.')
        return redirect('opportunity_list')

    so = SavedOpportunity.objects.filter(student=sp, opportunity=opp)
    if so.exists():
        so.delete()
        messages.success(request, 'Opportunity removed from saved list.')
    else:
        SavedOpportunity.objects.create(student=sp, opportunity=opp)
        Notification.objects.create(
            student=sp,
            message=f'You saved opportunity: {opp.company} - {opp.role}',
            date=timezone.now()
        )
        messages.success(request, 'Opportunity saved.')
    return redirect('opportunity_detail', pk=pk)

# -------------------------------
# Apply
# -------------------------------
@login_required
@student_required
def apply_opportunity(request, pk):
    opp = get_object_or_404(CareerOpportunity, pk=pk)
    sp = get_student_profile_for_request(request)
    if not sp:
        messages.error(request, 'Student profile not found.')
        return redirect('opportunity_list')

    # Check if already applied
    if Application.objects.filter(student=sp, opportunity=opp).exists():
        messages.warning(request, 'You already applied to this opportunity.')
        return redirect('opportunity_detail', pk=pk)

    # Create new application directly
    app = Application.objects.create(
        student=sp,
        opportunity=opp,
        date_applied=timezone.now()
    )

    Notification.objects.create(
        student=sp,
        message=f'Application sent for: {opp.company} - {opp.role}',
        date=timezone.now()
    )
    messages.success(request, 'Application submitted successfully.')

    return redirect('opportunity_detail', pk=pk)


# -------------------------------
# Notifications
# -------------------------------
@login_required
@student_required
def notifications_view(request):
    sp = get_student_profile_for_request(request)
    notifications = []
    if sp:
        Notification.objects.filter(student=sp, read=False).update(read=True)
        notifications = Notification.objects.filter(student=sp).order_by('-date')[:20]
    return render(request, 'careers/notifications.html', {'notifications': notifications})

# -------------------------------
# Register User
# -------------------------------
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role', 'student')
            UserProfile.objects.get_or_create(user=user, defaults={'role': role})
            if role == 'student':
                StudentProfile.objects.get_or_create(user=user)
            login(request, user)
            if role == 'lecturer':
                return redirect('manage_opportunities')
            return redirect('opportunity_list')
    else:
        form = RegistrationForm()
    return render(request, 'careers/register.html', {'form': form})

# -------------------------------
# Edit Profile
# -------------------------------
@login_required
@student_required
def edit_profile(request):
    sp = get_student_profile_for_request(request)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=sp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('opportunity_list')
    else:
        form = ProfileForm(instance=sp)
    return render(request, 'careers/edit_profile.html', {'form': form})

# -------------------------------
# Profile Redirect
# -------------------------------
def profile_redirect(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
            if profile.role == 'lecturer':
                return redirect('manage_opportunities')
        except (AttributeError, UserProfile.DoesNotExist):
            pass
        return redirect('opportunity_list')
    return redirect('login')

# -------------------------------
# Lecturer: Manage Opportunities
# -------------------------------
@login_required
@lecturer_required
def manage_opportunities(request):
    # Fetch opportunities posted by the logged-in lecturer
    opportunities = CareerOpportunity.objects.filter(
        posted_by=request.user
    ).order_by('-created_at')

    # Add computed attributes for template display
    for opp in opportunities:
        # Get all applications for this opportunity
        applications = opp.applications.all()

        # Get all students who have already been graded for this opportunity
        graded_students = StudentGrade.objects.filter(opportunity=opp).values_list('student_id', flat=True)

        # Count students who applied but not yet graded
        pending_count = applications.exclude(student_id__in=graded_students).count()

        # Attach computed count to the opportunity instance
        opp.pending_count = pending_count

    return render(request, 'careers/manage_opportunities.html', {
        'opportunities': opportunities,
        'show_add_button': True
    })





@login_required
@lecturer_required
def create_opportunity(request):
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opp = form.save(commit=False)
            opp.posted_by = request.user
            opp.save()
            messages.success(request, 'Opportunity posted successfully!')
            return redirect('manage_opportunities')
    else:
        form = OpportunityForm()
    return render(request, 'careers/create_opportunity.html', {'form': form})

@login_required
@lecturer_required
def edit_opportunity(request, pk):
    opp = get_object_or_404(CareerOpportunity, pk=pk, posted_by=request.user)
    if request.method == 'POST':
        form = OpportunityForm(request.POST, instance=opp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Opportunity updated successfully!')
            return redirect('manage_opportunities')
    else:
        form = OpportunityForm(instance=opp)
    return render(request, 'careers/create_opportunity.html', {'form': form, 'edit': True})

@login_required
@lecturer_required
def delete_opportunity(request, pk):
    opp = get_object_or_404(CareerOpportunity, pk=pk, posted_by=request.user)
    if request.method == 'POST':
        opp.delete()
        messages.success(request, 'Opportunity deleted successfully!')
        return redirect('manage_opportunities')
    return render(request, 'careers/delete_confirmation.html', {'opp': opp})

# -------------------------------
# Lecturer: View Applicants
# -------------------------------
@login_required
@lecturer_required
def view_applicants(request, pk):
    opp = get_object_or_404(CareerOpportunity, pk=pk, posted_by=request.user)
    applications = Application.objects.filter(opportunity=opp).select_related('student__user').order_by('-applied_at')

    for app in applications:
        grades = StudentGrade.objects.filter(student=app.student)
        summary = compute_gpa_summary(grades)
        app.student.gpa = summary.get('gpa', None)
        app.student.cgpa = summary.get('cgpa', None)

    gpas = [app.student.gpa for app in applications if app.student.gpa]
    avg_gpa = round(sum(gpas) / len(gpas), 2) if gpas else None

    return render(request, 'careers/view_applicants.html', {
        'opp': opp,
        'applications': applications,
        'avg_gpa': avg_gpa,
    })

# -------------------------------
# Export Applicants to CSV
# -------------------------------
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from careers.models import StudentProfile, StudentGrade, Semester

import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from careers.models import StudentProfile, StudentGrade, Semester
from careers.utils.grades import compute_gpa_summary

@login_required
def download_student_grades_csv(request, student_id=None, semester_id=None):
    """
    Download CSV of student grades.
    If semester_id is provided, download grades for that semester only.
    If student_id is provided, download for that specific student.
    Otherwise, download all grades for all students.
    """

    # Prepare the response as CSV
    response = HttpResponse(content_type='text/csv')
    filename = "student_grades.csv"
    if semester_id:
        semester = Semester.objects.get(id=semester_id)
        filename = f"{semester.year}_{semester.get_name_display()}_grades.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    
    # CSV Header
    header = ['Student Name', 'Reg No', 'Semester', 'Subject', 'Credit Units', 'Score', 'Grade', 'GPA', 'CGPA']
    writer.writerow(header)

    # Fetch grades
    grades_qs = StudentGrade.objects.all()
    if student_id:
        grades_qs = grades_qs.filter(student__id=student_id)
    if semester_id:
        grades_qs = grades_qs.filter(semester__id=semester_id)

    # Group grades by student and semester
    students = set(grades_qs.values_list('student_id', flat=True))
    for sid in students:
        student = StudentProfile.objects.get(id=sid)
        student_grades = grades_qs.filter(student=student)
        semesters = set(student_grades.values_list('semester_id', flat=True))
        for sem_id in semesters:
            sem = Semester.objects.get(id=sem_id) if sem_id else None
            sem_grades = student_grades.filter(semester_id=sem_id)
            
            # Compute GPA and CGPA
            gpa_summary = compute_gpa_summary(sem_grades)
            gpa = gpa_summary.get('gpa', 0.0)
            cgpa = gpa_summary.get('cgpa', 0.0)

            for grade in sem_grades:
                writer.writerow([
                    student.user.get_full_name,
                    student.user.username,
                    f"{sem.year} - {sem.get_name_display()}" if sem else "N/A",
                    grade.course_unit,
                    getattr(grade, 'credit_units', 0),
                    grade.score,
                    grade.grade,
                    gpa,
                    cgpa
                ])

    return response


# -------------------------------
# Lecturer: Enter Grades (NEW)
# -------------------------------
@login_required
@lecturer_required
def enter_course_grades(request, course_id):
    course = get_object_or_404(CareerOpportunity, id=course_id)
    # Only allow lecturer who posted this course
    if course.posted_by != request.user:
        messages.error(request, 'You are not authorized to enter grades for this course.')
        return redirect('manage_opportunities')

    # Get all students who applied for this course
    applications = Application.objects.filter(opportunity=course).select_related('student__user')

    if request.method == 'POST':
        for app in applications:
            grade_value = request.POST.get(f'grade_{app.student.id}')
            if grade_value:
                StudentGrade.objects.update_or_create(
                    student=app.student,
                    opportunity=course,
                    defaults={'grade': grade_value}
                )
        messages.success(request, 'Grades updated successfully.')
        return redirect('view_applicants', pk=course.id)

    return render(request, 'lecturer/enter_grades.html', {
        'course': course,
        'applications': applications
    })

# -------------------------------
# Admin Management Views
# -------------------------------
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from careers.models import UserProfile, StudentProfile, StudentGrade, Semester

@user_passes_test(lambda u: u.is_staff)
def admin_student_list(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    # Fetch all students with related user object
    students = UserProfile.objects.filter(role='student').select_related('user')

    # Apply search query
    if query:
        students = students.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query)
        )

    # Apply active/inactive filter
    if status_filter == 'active':
        students = students.filter(user__is_active=True)
    elif status_filter == 'inactive':
        students = students.filter(user__is_active=False)

    # Compute GPA and CGPA using StudentGrade model methods
    for student in students:
        try:
            sp = student.user.studentprofile

            # Latest semester for GPA
            latest_semester = Semester.objects.order_by('-year', '-name').first()

            student.gpa = StudentGrade.calculate_gpa(sp, latest_semester) if latest_semester else None
            student.cgpa = StudentGrade.calculate_cgpa(sp)

        except StudentProfile.DoesNotExist:
            student.gpa = None
            student.cgpa = None

    context = {
        'students': students,
        'q': query,
        'status_filter': status_filter
    }

    return render(request, 'careers/admin_student_list.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_lecturer_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    lecturers = UserProfile.objects.filter(role='lecturer').select_related('user')

    if query:
        lecturers = lecturers.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query)
        )

    if status_filter == 'active':
        lecturers = lecturers.filter(user__is_active=True)
    elif status_filter == 'inactive':
        lecturers = lecturers.filter(user__is_active=False)

    return render(request, 'careers/admin_lecturer_list.html', {
        'lecturers': lecturers,
        'q': query,
        'status_filter': status_filter
    })

from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from .models import UserProfile, CareerOpportunity, Application, GeneratedReport
from django.contrib.auth.models import User

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    total_users = User.objects.count()
    total_students = UserProfile.objects.filter(role='student').count()
    total_lecturers = UserProfile.objects.filter(role='lecturer').count()
    total_opportunities = CareerOpportunity.objects.count()
    total_applications = Application.objects.count()

    profiles = UserProfile.objects.select_related('user').annotate(
        posted_count=Count('user__posted_opportunities'),
    )

    # Latest report (any status)
    latest_report = GeneratedReport.objects.filter(generated_by=request.user).order_by('-generated_at').first()

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_opportunities': total_opportunities,
        'total_applications': total_applications,
        'profiles': profiles,
        'latest_report': latest_report,
    }

    return render(request, 'careers/admin_dashboard.html', context)



@user_passes_test(lambda u: u.is_staff)
def admin_toggle_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f"{user.username}'s account has been {'activated' if user.is_active else 'deactivated'}.")
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

@login_required
@lecturer_required
def view_student_performance(request, student_id):
    student_profile = get_object_or_404(StudentProfile, id=student_id)
    
    # Fetch all grades for this student
    grades_qs = StudentGrade.objects.filter(student=student_profile)
    gpa_summary = compute_gpa_summary(grades_qs)
    
    context = {
        'student': student_profile,
        'grades': grades_qs,
        'gpa': gpa_summary.get('gpa'),
        'cgpa': gpa_summary.get('cgpa'),
    }
    return render(request, 'lecturer/view_student_performance.html', context)


    # careers/views.py
import threading
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


def staff_required(user):
    return user.is_staff



import os
import csv
import threading
from datetime import datetime  # ✅ use this
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CareerOpportunity, GeneratedReport

@login_required
@user_passes_test(lambda u: u.is_staff)
def generate_reports(request):
    """
    Generate report asynchronously in a separate thread.
    """
    def generate_report_thread(user):
        report_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(report_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file_name = f'career_opportunities_report_{timestamp}.csv'
        report_file_path = os.path.join(report_dir, report_file_name)

        # Create report entry as "generating"
        report = GeneratedReport.objects.create(
            file=f'reports/{report_file_name}',
            generated_by=user,
            status='generating'
        )

        try:
            with open(report_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Company', 'Role', 'Deadline', 'Field', 'Posted By'])
                for opp in CareerOpportunity.objects.all():
                    writer.writerow([
                        opp.company,
                        opp.role,
                        opp.deadline,
                        opp.field,
                        opp.posted_by.username if opp.posted_by else 'N/A'
                    ])

            # Mark as ready
            report.status = 'ready'
            report.save()

        except Exception as e:
            report.status = 'error'
            report.save()

    # Start report generation in background thread
    threading.Thread(target=generate_report_thread, args=(request.user,)).start()

    messages.success(request, "Report generation started. Please wait for it to finish!")
    return redirect('admin_dashboard')


# careers/views.py
from django.http import FileResponse, Http404


@login_required
@user_passes_test(lambda u: u.is_staff)
def download_latest_report(request, report_id):
    try:
        report = GeneratedReport.objects.get(id=report_id, generated_by=request.user)
        response = FileResponse(open(report.file.path, 'rb'), as_attachment=True, filename=f"{report.file.name}")
        
        # Optional: delete the report after download
        report.file.delete(save=False)  # deletes the file from storage
        report.delete()  # deletes the database record
        return response
    except GeneratedReport.DoesNotExist:
        raise Http404("Report not found")


from django.http import JsonResponse
from .models import GeneratedReport
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import EnterGradeForm

@login_required
@user_passes_test(lambda u: u.is_staff)
def check_report_status(request, report_id):
    """
    Returns the status of a report in JSON: generating, ready, or error
    """
    try:
        report = GeneratedReport.objects.get(id=report_id, generated_by=request.user)
        return JsonResponse({'status': report.status})
    except GeneratedReport.DoesNotExist:
        return JsonResponse({'status': 'error'})


@login_required
@lecturer_required
def lecturer_student_list(request, pk):
    """
    Displays the list of students who applied for a specific opportunity/course.
    Lecturer can enter or update grades for each student.
    """
    # Get the opportunity/course
    opportunity = get_object_or_404(CareerOpportunity, pk=pk, posted_by=request.user)

    # Get all applications for this opportunity
    applications = Application.objects.filter(opportunity=opportunity).select_related('student__user').order_by('-applied_at')

    # Compute GPA/CGPA for each student
    for app in applications:
        grades = StudentGrade.objects.filter(student=app.student)
        summary = compute_gpa_summary(grades)
        app.student.gpa = summary.get('gpa', None)
        app.student.cgpa = summary.get('cgpa', None)

    # Average GPA across applicants (optional)
    gpas = [app.student.gpa for app in applications if app.student.gpa]
    avg_gpa = round(sum(gpas) / len(gpas), 2) if gpas else None

    context = {
        'opportunity': opportunity,
        'applications': applications,
        'avg_gpa': avg_gpa,
    }

    return render(request, 'careers/lecturer_student_list.html', context)


@login_required
@lecturer_required
def lecturer_students_list(request, opp_id=None):
    """
    Displays students. If opp_id is provided and >0, filter by that opportunity.
    """
    if opp_id and int(opp_id) > 0:
        # Students who applied for this opportunity
        applications = Application.objects.filter(opportunity_id=opp_id)
        students = StudentProfile.objects.filter(id__in=applications.values_list('student_id', flat=True))
    else:
        # All students
        students = StudentProfile.objects.all()

    return render(request, 'careers/lecturer_student_list.html', {
        'students': students,
        'opp_id': opp_id,
    })


@login_required
@lecturer_required
def lecturer_student_list_all(request):
    """
    View for lecturers to see all students registered in the system.
    """
    students = StudentProfile.objects.all().order_by('user__last_name', 'user__first_name')
    return render(request, 'careers/lecturer_student_list.html', {
        'students': students,
        'show_all': True  # optional flag for template
    })





from django.urls import reverse
from .models import Semester
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from careers.models import StudentProfile, StudentGrade, Semester
from careers.utils.grades import get_grade_point

@login_required
def enter_grades(request, student_id, opp_id=None):
    student = get_object_or_404(StudentProfile, pk=student_id)
    semesters = Semester.objects.all().order_by('-year', 'name')

    # Selected semester (default to first if none)
    selected_semester_id = request.GET.get('semester')
    selected_semester = Semester.objects.filter(id=selected_semester_id).first() if selected_semester_id else semesters.first()

    if request.method == 'POST':
        subjects = request.POST.getlist('subject[]')
        scores = request.POST.getlist('score[]')
        semester_id = request.POST.get('semester')
        semester = get_object_or_404(Semester, pk=semester_id)

        # Save grades
        for i in range(len(subjects)):
            subject = subjects[i].strip()
            score = float(scores[i]) if scores[i] else 0
            if subject:
                StudentGrade.objects.update_or_create(
                    student=student,
                    course_unit=subject,
                    semester=semester,
                    defaults={
                        'score': score,
                        'opportunity': None
                    }
                )

        messages.success(request, f"Grades for {semester.name} successfully saved!")
        redirect_url = f"/careers/lecturer/student/{student.id}/enter-grades/?semester={semester.id}"
        if opp_id:
            redirect_url += f"&opp_id={opp_id}"
        return redirect(redirect_url)

    # Fetch grades for the selected semester
    grades_queryset = StudentGrade.objects.filter(student=student)
    if selected_semester:
        grades_queryset = grades_queryset.filter(semester=selected_semester)

    # --- Compute GPA & CGPA manually using 'score' field only ---
    total_points = 0
    total_courses = 0
    for grade in grades_queryset:
        _, point = get_grade_point(grade.score)  # get numeric grade point
        total_points += point
        total_courses += 1

    gpa = round(total_points / total_courses, 2) if total_courses else 0.0
    # CGPA: average across all grades for this student
    all_grades = StudentGrade.objects.filter(student=student)
    total_points_all = sum(get_grade_point(g.score)[1] for g in all_grades)
    total_courses_all = all_grades.count()
    cgpa = round(total_points_all / total_courses_all, 2) if total_courses_all else 0.0

    # Organize past grades per semester
    past_grades = {}
    for sem in semesters:
        sem_grades = StudentGrade.objects.filter(student=student, semester=sem)
        if sem_grades.exists():
            past_grades[sem] = sem_grades

    return render(request, 'careers/enter_grades.html', {
        'student': student,
        'grades': grades_queryset,
        'semesters': semesters,
        'selected_semester': selected_semester,
        'past_grades': past_grades,
        'summary': {'gpa': gpa, 'cgpa': cgpa},
        'opp_id': opp_id
    })


import csv
import threading
import tempfile
from django.http import FileResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import StudentProfile, StudentGrade

# ---------------------------
# Async function to generate all students report
# ---------------------------
def generate_all_students_report():
    # Create a temporary file
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    writer = csv.writer(tmp_file)
    
    # Header row
    writer.writerow([
        'Student Name', 'Username', 'Course Unit', 'Semester', 
        'Score', 'Grade', 'Grade Points'
    ])
    
    students = StudentProfile.objects.prefetch_related('grades__semester').all()
    for student in students:
        grades = student.grades.all().select_related('semester')
        for grade in grades:
            writer.writerow([
                student.user.get_full_name(),
                student.user.username,
                grade.course_unit,
                f"{grade.semester.year} - {grade.semester.name}" if grade.semester else "N/A",
                grade.score,
                grade.grade,
                grade.grade_points
            ])
    tmp_file.close()
    return tmp_file.name



@user_passes_test(lambda u: u.is_staff)
def admin_generate_all_students_report(request):
    try:
        # Create HTTP response for CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="all_students_report.csv"'

        writer = csv.writer(response)
        # Header row
        writer.writerow([
            'Username', 'Full Name', 'Email', 'Semester', 
            'Subject', 'Score', 'Grade', 'Credit Units', 'Grade Points'
        ])

        # Fetch all students
        students = StudentProfile.objects.select_related('user').all()

        # Function to write student data
        def write_student_data():
            for student in students:
                grades = StudentGrade.objects.filter(student=student).select_related('semester').order_by('semester__year', 'semester__name')
                for grade in grades:
                    writer.writerow([
                        student.user.username,
                        f"{student.user.first_name} {student.user.last_name}",
                        student.user.email,
                        f"{grade.semester.year} - {grade.semester.name}" if grade.semester else "N/A",
                        grade.course_unit,
                        grade.score,
                        grade.grade,
                        grade.credit_units,
                        grade.grade_points
                    ])

        # Run writing in a separate thread to avoid blocking (asynchronous)
        thread = threading.Thread(target=write_student_data)
        thread.start()
        thread.join()  # Wait for thread to finish before returning response

        return response

    except Exception as e:
        # Log error for debugging
        print(f"Error generating report: {e}")
        return HttpResponse("Error generating report", status=500)



@staff_member_required
def all_students_performance(request):
    students = StudentProfile.objects.prefetch_related('grades__semester').all()
    context = {
        'students': students,
    }
    return render(request, 'careers/admin_all_students_performance.html', context)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = StudentProfile.objects.filter(user=user).first()
        if not profile:
            return Response({'detail': 'Profile not found'}, status=404)

        grades = StudentGrade.objects.filter(student=profile)
        grade_list = [
            {
                'course_unit': g.course_unit,
                'score': g.score,
                'grade': g.grade,
                'semester': str(g.semester),
            }
            for g in grades
        ]

        data = {
            'username': user.username,
            'full_name': user.get_full_name(),
            'email': user.email,
            'gpa': profile.gpa if hasattr(profile, 'gpa') else None,
            'grades': grade_list,
        }
        return Response(data)



