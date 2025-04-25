from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .filters import JobFilter
from .models import Application, Job, Review
from .serializers import (
    ApplicationListSerializer,
    ApplicationSerializer,
    ApplicationWithFreelancerSerializer,
    HiredSerializer,
    JobSerializer,
    ReviewSerializer,
)
from accounts.permissions import IsClient, IsFreelancer, IsJobOwner
from django.utils import timezone
from django.core.exceptions import PermissionDenied


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
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    def get_queryset(self):
        return Job.objects.filter(client=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient, IsJobOwner]


class PublicJobListView(generics.ListAPIView):
    queryset = Job.objects.filter(
        is_open=True,
    )
    serializer_class = JobSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = JobFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "budget"]
    permission_classes = [permissions.AllowAny]
    ordering = ["-created_at"]


class AppliedJobsListView(generics.ListAPIView):
    serializer_class = ApplicationListSerializer
    permission_classes = [permissions.IsAuthenticated, IsFreelancer]
    ordering = ["-created_at"]

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


class JobApplicantsView(generics.ListAPIView):
    serializer_class = ApplicationWithFreelancerSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]

    def get_queryset(self):
        job_id = self.kwargs["job_id"]
        job = get_object_or_404(Job, id=job_id, client=self.request.user)
        return Application.objects.filter(job=job).select_related("freelancer")


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsClient],
    )
    def hire(self, request, pk=None):
        application = self.get_object()
        job = application.job

        # Make sure only the job's owner (client) can hire
        if job.client != request.user:
            return Response(
                {"detail": "You do not own this job."}, status=status.HTTP_403_FORBIDDEN
            )

        # Make sure job is still active
        # if not job.is_active:
        #     return Response(
        #         {"detail": "This job is already closed."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # Prevent hiring more than one freelancer
        if Application.objects.filter(job=job, is_hired=True).exists():
            return Response(
                {"detail": "A freelancer is already hired for this job."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.is_hired = True
        application.hired_date = timezone.now()
        application.save()

        # Optional: mark job as closed
        job.is_open = False
        job.save()

        return Response({"message": "Freelancer hired successfully!"})

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def hired(self, request):
        hired_apps = Application.objects.filter(
            is_hired=True, job__client=request.user
        ).select_related("job", "freelancer")

        serializer = HiredSerializer(hired_apps, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        job = serializer.validated_data["job"]
        freelancer = serializer.validated_data["freelancer"]

        # Check: is the user the client of this job?
        if job.client != self.request.user:
            raise PermissionDenied("You can only review freelancers for your own jobs.")

        # Check: was the freelancer hired for this job?
        if not Application.objects.filter(
            job=job, freelancer=freelancer, is_hired=True
        ).exists():
            raise ValidationError("You can only review freelancers you have hired.")

        serializer.save(client=self.request.user)

    def perform_list(self, serializer):
        # Only show reviews for the logged-in user's jobs
        self.queryset = self.queryset.filter(client=self.request.user)
        return super().perform_list(serializer)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def reply(self, request, pk=None):
        review = self.get_object()

        if review.freelancer != request.user:
            raise PermissionDenied("You can only reply to reviews written about you.")

        reply_text = request.data.get("reply", "").strip()
        if not reply_text:
            raise ValidationError({"reply": "Reply cannot be empty."})

        review.reply = reply_text
        review.save()

        return Response({"message": "Reply added successfully."})
