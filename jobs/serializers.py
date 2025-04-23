from rest_framework import serializers
from .models import Application, Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "title", "description", "budget", "created_at", "is_open"]


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
