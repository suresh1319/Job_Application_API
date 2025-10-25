from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone


class Applicant(models.Model):
    """Model to store applicant information."""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    applied_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta:
        ordering = ['-applied_on']


class Job(models.Model):
    """Model to store job postings."""
    title = models.CharField(max_length=100)
    description = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-posted_on']


class Application(models.Model):
    """Model to track job applications."""
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
    ]

    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied'
    )
    applied_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant.name} - {self.job.title} ({self.status})"

    class Meta:
        ordering = ['-applied_on']
        unique_together = ['applicant', 'job']

    def clean(self):
        from django.core.exceptions import ValidationError
        # Check if the job is active
        if not self.job.is_active:
            raise ValidationError("Cannot apply to an inactive job")
        
        # Check for duplicate application
        if self._state.adding and Application.objects.filter(
            applicant=self.applicant,
            job=self.job
        ).exists():
            raise ValidationError("You have already applied to this job")
