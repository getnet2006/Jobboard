from django.urls import path
from .views import JobCreateListView

urlpatterns = [
    path("", JobCreateListView.as_view(), name="job-list-create"),
]
