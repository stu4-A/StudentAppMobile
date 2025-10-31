# careers/api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from ..models import (
    UserProfile, StudentProfile, CareerOpportunity, SavedOpportunity,
    Application, Notification, Semester, CourseUnit, StudentGrade, GeneratedReport
)
from .serializers import (
    UserProfileSerializer, StudentProfileSerializer, CareerOpportunitySerializer,
    SavedOpportunitySerializer, ApplicationSerializer, NotificationSerializer,
    SemesterSerializer, CourseUnitSerializer, StudentGradeSerializer, GeneratedReportSerializer
)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current user's profile"""
        profile = UserProfile.objects.get(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_student_profile(self, request):
        """Get current user's student profile"""
        try:
            profile = StudentProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {"error": "Student profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class CareerOpportunityViewSet(viewsets.ModelViewSet):
    queryset = CareerOpportunity.objects.all().order_by('-created_at')
    serializer_class = CareerOpportunitySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def save_opportunity(self, request, pk=None):
        """Save opportunity for current student"""
        opportunity = self.get_object()
        student_profile = StudentProfile.objects.get(user=request.user)
        
        saved_opp, created = SavedOpportunity.objects.get_or_create(
            student=student_profile,
            opportunity=opportunity
        )
        
        if created:
            return Response({"message": "Opportunity saved successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Opportunity already saved"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply for an opportunity"""
        opportunity = self.get_object()
        student_profile = StudentProfile.objects.get(user=request.user)
        
        application, created = Application.objects.get_or_create(
            student=student_profile,
            opportunity=opportunity,
            defaults={'cover_letter': request.data.get('cover_letter', '')}
        )
        
        if created:
            return Response({"message": "Application submitted successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Already applied for this opportunity"}, status=status.HTTP_200_OK)

class SavedOpportunityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only saved opportunities for current user"""
        student_profile = StudentProfile.objects.get(user=self.request.user)
        return SavedOpportunity.objects.filter(student=student_profile)

    serializer_class = SavedOpportunitySerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only applications for current user"""
        student_profile = StudentProfile.objects.get(user=self.request.user)
        return Application.objects.filter(student=student_profile)

    serializer_class = ApplicationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only notifications for current user"""
        student_profile = StudentProfile.objects.get(user=self.request.user)
        return Notification.objects.filter(student=student_profile).order_by('-date')

    serializer_class = NotificationSerializer

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({"message": "Notification marked as read"})

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated]

class CourseUnitViewSet(viewsets.ModelViewSet):
    queryset = CourseUnit.objects.all()
    serializer_class = CourseUnitSerializer
    permission_classes = [IsAuthenticated]

class StudentGradeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return grades for current user"""
        student_profile = StudentProfile.objects.get(user=self.request.user)
        return StudentGrade.objects.filter(student=student_profile)

    serializer_class = StudentGradeSerializer

    @action(detail=False, methods=['get'])
    def my_gpa(self, request):
        """Get current student's GPA and CGPA"""
        student_profile = StudentProfile.objects.get(user=request.user)
        
        # Update student profile GPA/CGPA
        student_profile.gpa = StudentGrade.calculate_gpa(student_profile, None)  # You might want to specify semester
        student_profile.cgpa = StudentGrade.calculate_cgpa(student_profile)
        student_profile.save()
        
        return Response({
            'gpa': student_profile.gpa,
            'cgpa': student_profile.cgpa
        })

class GeneratedReportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return reports generated by current user"""
        return GeneratedReport.objects.filter(generated_by=self.request.user)

    serializer_class = GeneratedReportSerializer

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Dashboard overview for current user"""
        user_profile = UserProfile.objects.get(user=request.user)
        student_profile = StudentProfile.objects.get(user=request.user)
        
        # Get recent opportunities
        recent_opportunities = CareerOpportunity.objects.all().order_by('-created_at')[:5]
        
        # Get user's applications
        user_applications = Application.objects.filter(student=student_profile)
        
        # Get unread notifications count
        unread_notifications = Notification.objects.filter(student=student_profile, read=False).count()
        
        # Get saved opportunities
        saved_opportunities = SavedOpportunity.objects.filter(student=student_profile).count()
        
        dashboard_data = {
            'user_profile': UserProfileSerializer(user_profile).data,
            'student_profile': StudentProfileSerializer(student_profile).data,
            'recent_opportunities': CareerOpportunitySerializer(recent_opportunities, many=True).data,
            'application_count': user_applications.count(),
            'unread_notifications': unread_notifications,
            'saved_opportunities_count': saved_opportunities,
        }
        
        return Response(dashboard_data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get detailed statistics for dashboard"""
        student_profile = StudentProfile.objects.get(user=request.user)
        
        # Calculate GPA stats
        gpa = student_profile.gpa
        cgpa = student_profile.cgpa
        
        # Get opportunities stats
        total_opportunities = CareerOpportunity.objects.count()
        applied_opportunities = Application.objects.filter(student=student_profile).count()
        saved_opportunities = SavedOpportunity.objects.filter(student=student_profile).count()
        
        stats_data = {
            'academic': {
                'gpa': gpa,
                'cgpa': cgpa,
                'total_courses': StudentGrade.objects.filter(student=student_profile).count()
            },
            'opportunities': {
                'total': total_opportunities,
                'applied': applied_opportunities,
                'saved': saved_opportunities
            }
        }
        
        return Response(stats_data)