from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import Applicant, Job, Application
from .serializers import (
    ApplicantSerializer,
    JobSerializer,
    ApplicationSerializer,
    ApplicationStatusUpdateSerializer
)


class ApplicantListCreateView(ListCreateAPIView):
    """
    View for listing and creating applicants.
    """
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'email']
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return []
        return [IsAuthenticated()]


class ApplicantDetailView(RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating and deleting an applicant.
    """
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [IsAuthenticated]


class JobListCreateView(ListCreateAPIView):
    """
    View for listing and creating jobs.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]


class JobDetailView(RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating and deleting a job.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]


class ApplicationListView(ListAPIView):
    """
    View for listing all applications.
    """
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'job__id', 'applicant__id']

    def get_queryset(self):
        # Regular users can only see their own applications
        if not self.request.user.is_staff:
            return Application.objects.filter(applicant__email=self.request.user.email)
        # Admin can see all applications
        return Application.objects.all()


class ApplicationCreateView(APIView):
    """
    View for creating a new application.
    """
    permission_classes = []  # Allow anyone to apply
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        # Get or create applicant
        email = request.data.get('email')
        if not email:
            return Response(
                {"email": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            applicant = Applicant.objects.get(email=email)
            # Update applicant data if provided
            for field in ['name', 'phone', 'resume']:
                if field in request.data:
                    setattr(applicant, field, request.data[field])
            applicant.save()
        except Applicant.DoesNotExist:
            # Create new applicant
            serializer = ApplicantSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            applicant = serializer.save()

        # Create application
        job_id = request.data.get('job')
        if not job_id:
            return Response(
                {"job": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            job = Job.objects.get(id=job_id, is_active=True)
        except Job.DoesNotExist:
            return Response(
                {"job": ["Job not found or inactive."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for duplicate application
        if Application.objects.filter(applicant=applicant, job=job).exists():
            return Response(
                {"detail": "You have already applied to this job."},
                status=status.HTTP_400_BAD_REQUEST
            )

        application = Application.objects.create(
            applicant=applicant,
            job=job,
            status='applied'
        )

        serializer = ApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApplicationStatusUpdateView(APIView):
    """
    View for updating application status (admin only).
    """
    permission_classes = [IsAdminUser]

    def patch(self, request, pk, format=None):
        try:
            application = Application.objects.get(pk=pk)
        except Application.DoesNotExist:
            return Response(
                {"detail": "Application not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ApplicationStatusUpdateSerializer(
            application,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
