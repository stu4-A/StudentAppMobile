from django.contrib import admin
from .models import StudentProfile, CareerOpportunity, SavedOpportunity, Application, Notification
from .models import Semester

admin.site.register(StudentProfile)
admin.site.register(CareerOpportunity)
admin.site.register(SavedOpportunity)
admin.site.register(Application)
admin.site.register(Notification)
admin.site.register(Semester)
