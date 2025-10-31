# careers/urls.py
from django.urls import path
from . import views
from careers.views import download_student_grades_csv


urlpatterns = [
    # Home & registration
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    #path('home/', views.home, name='home'),
    
    

    # ----------------------------
    # Student URLs
    # ----------------------------
    path('list/', views.opportunity_list, name='opportunity_list'),
    path('opportunity/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunity/<int:pk>/save_toggle/', views.save_toggle, name='save_toggle'),
    path('opportunity/<int:pk>/apply/', views.apply_opportunity, name='apply_opportunity'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('profile/', views.edit_profile, name='edit_profile'),


    # ----------------------------
    # Lecturer URLs
    # ----------------------------
    path('manage/', views.manage_opportunities, name='manage_opportunities'),
    path('manage/create/', views.create_opportunity, name='create_opportunity'),
    path('manage/<int:pk>/edit/', views.edit_opportunity, name='edit_opportunity'),
    path('manage/<int:pk>/delete/', views.delete_opportunity, name='delete_opportunity'),
    path('manage/<int:pk>/applications/', views.view_applicants, name='view_applicants'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-toggle-user/<int:user_id>/', views.admin_toggle_user, name='admin_toggle_user'),
    path('admin/generate-reports/', views.generate_reports, name='generate_reports'),
     path('download-latest-report/<int:report_id>/', views.download_latest_report, name='download_latest_report'),
        
    path('admin/students/', views.admin_student_list, name='admin_student_list'),
    path('admin/lecturers/', views.admin_lecturer_list, name='admin_lecturer_list'),
    path('lecturer/course/<int:course_id>/enter-grades/', views.enter_course_grades, name='enter_course_grades'),
    path('lecturer/student/<int:student_id>/performance/', views.view_student_performance,name='view_student_performance'),
    path('lecturer/student/<int:student_id>/opportunity/<int:opportunity_id>/grades/',views.enter_grades,name='enter_grades'),

    # Export applicants to CSV
    

    # View applicants
    path('manage/<int:pk>/applications/', views.view_applicants, name='view_applicants'),

    

    # Enter grades (example)
    path('manage/<int:opp_id>/applicants/<int:student_id>/enter-grades/',views.enter_grades, name='enter_grades'), 
    path('lecturer/<int:opp_id>/students/', views.lecturer_student_list, name='lecturer_student_list'),
        
    path('lecturer/students/', views.lecturer_students_list, name='lecturer_students_list'),
    path('lecturer/student/<int:student_id>/enter-grades/', views.enter_grades, name='enter_student_grades'),
    path('lecturer/students/', views.lecturer_student_list_all, name='lecturer_student_list_all'),
    path('admin/students/performance/', views.all_students_performance, name='admin_all_students_performance'),
    path('admin/students/report/<int:student_id>/', views.admin_generate_all_students_report, name='admin_generate_student_report'),
    path('admin/students/report/all/', views.admin_generate_all_students_report, name='admin_generate_all_students_report'),
    path('admin/students/report/', views.admin_generate_all_students_report, name='admin_generate_all_students_report'),

    path('lecturer/grades/download/', download_student_grades_csv, name='download_student_grades_csv'),
    path('lecturer/grades/download/<int:semester_id>/', download_student_grades_csv, name='download_student_grades_csv_semester')
    

]
