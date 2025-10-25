"""
URL configuration for jobportal project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Schema view for API documentation
schema_view = get_schema_view(
   openapi.Info(
      title="Job Portal API",
      default_version='v1',
      description="API for Job Application Management System",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,  # Make schema accessible without authentication
   permission_classes=(permissions.AllowAny,),  # Allow any access to schema
   authentication_classes=(),
   validators=['flex', 'ssv'],
)

# Create a staff-required view for Swagger UI
staff_required = user_passes_test(lambda u: u.is_staff, login_url='admin:login')
swagger_view = login_required(staff_required(schema_view.with_ui('swagger', cache_timeout=0)))
redoc_view = login_required(staff_required(schema_view.with_ui('redoc', cache_timeout=0)))

urlpatterns = [
    # Redirect root URL to Swagger UI
    path('', RedirectView.as_view(url='swagger/', permanent=False)),
    
    # Admin login
    path('admin/login/', LoginView.as_view(template_name='admin/login.html', extra_context={'title': 'Login'}), name='login'),
    path('admin/', admin.site.urls),
    
    # API Documentation - these must come before other URL patterns
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', swagger_view, name='schema-swagger-ui'),
    path('redoc/', redoc_view, name='schema-redoc'),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Application URLs
    path('api/', include('applications.urls')),
    
    # Add a catch-all for /accounts/login/ to redirect to admin login
    path('accounts/login/', RedirectView.as_view(url='/admin/login/', permanent=False)),
]
