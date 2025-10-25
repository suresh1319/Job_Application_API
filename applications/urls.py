from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'applications'

router = DefaultRouter()

urlpatterns = [
    # Applicant endpoints
    path('applicants/', views.ApplicantListCreateView.as_view(), name='applicant-list-create'),
    path('applicants/<int:pk>/', views.ApplicantDetailView.as_view(), name='applicant-detail'),
    
    # Job endpoints
    path('jobs/', views.JobListCreateView.as_view(), name='job-list-create'),
    path('jobs/<int:pk>/', views.JobDetailView.as_view(), name='job-detail'),
    
    # Application endpoints
    path('apply/', views.ApplicationCreateView.as_view(), name='apply-job'),
    path('applications/', views.ApplicationListView.as_view(), name='application-list'),
    path('applications/<int:pk>/status/', views.ApplicationStatusUpdateView.as_view(), name='update-application-status'),
]
