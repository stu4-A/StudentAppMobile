# careers/helpers.py

from .models import StudentProfile

def get_student_profile_for_request(request):
    """
    Retrieves the StudentProfile for the currently logged-in user.
    Returns None if the user does not have a student profile.
    """
    if not request.user.is_authenticated:
        return None

    try:
        # Check if the user has a linked student profile
        if hasattr(request.user, 'studentprofile'):
            return request.user.studentprofile
        return StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return None
