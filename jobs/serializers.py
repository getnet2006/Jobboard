from rest_framework import serializers

from .models import Application, Job
from accounts.models import User


class JobSerializer(serializers.ModelSerializer):
    applicant_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "budget",
            "max_applications",
            "is_open",
            "created_at",
            "applicant_count",
        ]
        read_only_fields = ["id", "is_open", "created_at", "applicant_count"]

    def get_applicant_count(self, obj):
        return Application.objects.filter(job=obj).count()


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = ["id", "job", "cover_letter", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        job = attrs.get("job")

        if Application.objects.filter(job=job, freelancer=user).exists():
            raise serializers.ValidationError("You have already applied to this job.")

        if Application.objects.filter(job=job).count() >= job.max_applications:
            job.is_open = False
            job.save()
            raise serializers.ValidationError(
                "This job is no longer accepting applications."
            )

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        return Application.objects.create(freelancer=user, **validated_data)


class JobMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "title", "budget", "created_at"]


class ApplicationListSerializer(serializers.ModelSerializer):
    job = JobMiniSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ["id", "job", "cover_letter", "created_at"]


class FreelancerMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]  # add more if needed


class ApplicationWithFreelancerSerializer(serializers.ModelSerializer):
    freelancer = FreelancerMiniSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ["id", "freelancer", "cover_letter", "created_at"]
