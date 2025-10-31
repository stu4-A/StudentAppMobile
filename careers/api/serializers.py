from rest_framework import serializers
from careers.models import (
    Profile, Course, StudentMark, Club, CareerOpportunity,
    Achievement, SupportTicket, CourseReview
)
# from careers.utils.grade_utils import calculate_gpa, calculate_cpa

# -------------------------------
# Profile Serializer
# -------------------------------
class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    gpa = serializers.SerializerMethodField()
    cpa = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'name', 'role', 'registration_number',
            'department', 'office_number', 'specialization', 'gpa', 'cpa'
        ]

    def get_gpa(self, obj):
        from careers.models import StudentMark
        marks = StudentMark.objects.filter(student=obj)
        try:
            return round(calculate_gpa(marks), 2)
        except Exception:
            return None

    def get_cpa(self, obj):
        try:
            return round(calculate_cpa(obj), 2)
        except Exception:
            return None


# -------------------------------
# Course Serializer
# -------------------------------
class CourseSerializer(serializers.ModelSerializer):
    lecturer_name = serializers.CharField(source='lecturer.name', read_only=True)
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'credit_units', 'lecturer_name', 'students_count']

    def get_students_count(self, obj):
        return obj.students.count()


# -------------------------------
# StudentMark Serializer
# -------------------------------
class StudentMarkSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.name', read_only=True)

    class Meta:
        model = StudentMark
        fields = [
            'id', 'student_name', 'course_name',
            'lecturer_name', 'score', 'grade', 'gpa', 'cpa'
        ]


# -------------------------------
# Achievement Serializer
# -------------------------------
class AchievementSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Achievement
        fields = ['id', 'student_name', 'title', 'description', 'is_public', 'created_at']


# -------------------------------
# SupportTicket Serializer
# -------------------------------
class SupportTicketSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = SupportTicket
        fields = ['id', 'title', 'description', 'status', 'student_name', 'created_at']


# -------------------------------
# Career Opportunities Serializer
# -------------------------------
class CareerOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerOpportunity
        fields = ['id', 'company', 'role', 'deadline', 'link', 'posted_at']


# -------------------------------
# CourseReview Serializer
# -------------------------------
class CourseReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = CourseReview
        fields = ['id', 'student_name', 'course_name', 'rating', 'comment', 'created_at']


# -------------------------------
# Unified Dashboard Serializer (for student mobile dashboard)
# -------------------------------
class StudentDashboardSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()
    marks = serializers.SerializerMethodField()
    achievements = serializers.SerializerMethodField()
    tickets = serializers.SerializerMethodField()
    gpa = serializers.SerializerMethodField()
    cpa = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'name', 'role', 'registration_number',
            'gpa', 'cpa', 'courses', 'marks', 'achievements', 'tickets'
        ]

    def get_courses(self, obj):
        enrolled = obj.enrolled_courses.all()
        return CourseSerializer(enrolled, many=True).data

    def get_marks(self, obj):
        marks = obj.marks.select_related('course', 'lecturer').all()
        return StudentMarkSerializer(marks, many=True).data

    def get_achievements(self, obj):
        ach = obj.achievement_set.all()
        return AchievementSerializer(ach, many=True).data

    def get_tickets(self, obj):
        tickets = obj.supportticket_set.all()
        return SupportTicketSerializer(tickets, many=True).data

    def get_gpa(self, obj):
        from careers.models import StudentMark
        marks = StudentMark.objects.filter(student=obj)
        try:
            return round(calculate_gpa(marks), 2)
        except Exception:
            return None

    def get_cpa(self, obj):
        try:
            return round(calculate_cpa(obj), 2)
        except Exception:
            return None
