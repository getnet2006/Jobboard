from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .filters import JobFilter
from .models import Application, Job
from .serializers import ApplicationListSerializer, ApplicationSerializer, JobSerializer
from accounts.permissions import IsClient, IsFreelancer, IsJobOwner


class JobCreateListView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_open", "budget"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "budget"]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    def get_queryset(self):
        return Job.objects.filter(client=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient, IsJobOwner]


class PublicJobListView(generics.ListAPIView):
    queryset = Job.objects.filter(is_open=True)
    serializer_class = JobSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = JobFilter  # ← Use custom filter here
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "budget"]
    permission_classes = [permissions.AllowAny]


class AppliedJobsListView(generics.ListAPIView):
    serializer_class = ApplicationListSerializer
    permission_classes = [permissions.IsAuthenticated, IsFreelancer]

    def get_queryset(self):
        return Application.objects.filter(freelancer=self.request.user).select_related(
            "job"
        )


class ApplyToJobView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsFreelancer]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            errors = exc.detail
            # Convert non_field_errors to single message
            if "non_field_errors" in errors:
                return Response({"message": errors["non_field_errors"][0]}, status=400)
            return Response({"message": "Validation failed."}, status=400)

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
