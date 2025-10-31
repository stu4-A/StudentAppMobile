from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, StudentProfileViewSet, 
    CareerOpportunityViewSet, SavedOpportunityViewSet,
    ApplicationViewSet, NotificationViewSet,
    SemesterViewSet, CourseUnitViewSet, StudentGradeViewSet,
    GeneratedReportViewSet, DashboardViewSet
)

router = DefaultRouter()
router.register(r'user-profiles', UserProfileViewSet)
router.register(r'student-profiles', StudentProfileViewSet)
router.register(r'opportunities', CareerOpportunityViewSet)
router.register(r'saved-opportunities', SavedOpportunityViewSet)
router.register(r'applications', ApplicationViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'semesters', SemesterViewSet)
router.register(r'course-units', CourseUnitViewSet)
router.register(r'grades', StudentGradeViewSet)
router.register(r'reports', GeneratedReportViewSet)
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = router.urls