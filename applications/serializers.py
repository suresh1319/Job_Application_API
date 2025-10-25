from rest_framework import serializers
from .models import Applicant, Job, Application


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ['id', 'name', 'email', 'phone', 'resume', 'applied_on']
        read_only_fields = ['id', 'applied_on']


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'posted_on', 'is_active']
        read_only_fields = ['id', 'posted_on']


class ApplicationSerializer(serializers.ModelSerializer):
    applicant_details = serializers.SerializerMethodField()
    job_details = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id', 'applicant', 'job', 'status',
            'applied_on', 'updated_at', 'applicant_details', 'job_details'
        ]
        read_only_fields = ['id', 'applied_on', 'updated_at', 'applicant_details', 'job_details']

    def get_applicant_details(self, obj):
        return {
            'name': obj.applicant.name,
            'email': obj.applicant.email,
            'phone': obj.applicant.phone
        }

    def get_job_details(self, obj):
        return {
            'title': obj.job.title,
            'description': obj.job.description,
            'is_active': obj.job.is_active
        }

    def validate(self, data):
        if self.instance and 'status' in data:
            # Only allow status updates for existing instances
            return data
            
        # For new applications, validate that the job is active
        job = data.get('job')
        if job and not job.is_active:
            raise serializers.ValidationError("Cannot apply to an inactive job")
            
        # Check for duplicate application
        if self.context['request'].method == 'POST':
            applicant = data.get('applicant')
            if applicant and Application.objects.filter(
                applicant=applicant,
                job=job
            ).exists():
                raise serializers.ValidationError("You have already applied to this job")
                
        return data


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
