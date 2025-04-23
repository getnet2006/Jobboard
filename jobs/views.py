from rest_framework import generics, permissions
from .models import Job
from .serializers import JobSerializer
from accounts.permissions import IsClient


class JobCreateListView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    def get_queryset(self):
        # Clients only see their own jobs
        return Job.objects.filter(client=self.request.user)
