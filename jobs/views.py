from rest_framework import generics, permissions

from jobs.filters import JobFilter
from .models import Job
from .serializers import JobSerializer
from accounts.permissions import IsClient, IsJobOwner
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


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
