from django.urls import path
from .views import JobCreateListView, JobDetailView

urlpatterns = [
    path("", JobCreateListView.as_view(), name="job-list-create"),
    path("<int:pk>/", JobDetailView.as_view(), name="job-detail"),
]
