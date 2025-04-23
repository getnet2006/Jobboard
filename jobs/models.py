from django.db import models
from django.conf import settings

class Job(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    job = models.ForeignKey(
        "Job", on_delete=models.CASCADE, related_name="applications"
    )
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cover_letter = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("job", "freelancer")  # Prevent duplicate applications

    def __str__(self):
        return f"{self.freelancer} applied to {self.job}"

