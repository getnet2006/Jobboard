from django.urls import path

from .views import (
    ApplyToJobView,
    JobApplicantsView,
    JobCreateListView,
    JobDetailView,
    PublicJobListView,
    AppliedJobsListView,
)

urlpatterns = [
    path("", JobCreateListView.as_view(), name="job-list-create"),
    path("<int:pk>/", JobDetailView.as_view(), name="job-detail"),
    path("apply/", ApplyToJobView.as_view(), name="apply-to-job"),
    path("public/", PublicJobListView.as_view(), name="public-job-list"),
    path("my-applications/", AppliedJobsListView.as_view(), name="job-applications"),
    path(
        "<int:job_id>/applicants/",
        JobApplicantsView.as_view(),
        name="job-applicants",
    ),
]
