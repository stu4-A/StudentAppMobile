# student_portal/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from careers.views import CustomLoginView
from careers import views as careers_views
from django.contrib.auth.views import LogoutView
from careers.views import admin_dashboard
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [

    # your app routes
    path('api/', include('careers.urls')),   # include this if your app has its own urls.py

    # JWT authentication routes
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Admin site
    path('admin/', admin.site.urls),
    path('',careers_views.home,name='home'),

    # Home page (main landing)
    path('careers/', include('careers.urls')),

    # Custom authentication views
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='login'), name='logout'),
    #path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]

# Static and media files for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
