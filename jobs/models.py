from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

User = settings.AUTH_USER_MODEL


class Job(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)
    max_applications = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.title


class Application(models.Model):
    job = models.ForeignKey(
        "Job", on_delete=models.CASCADE, related_name="applications"
    )
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cover_letter = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    hired_date = models.DateTimeField(null=True, blank=True)
    is_hired = models.BooleanField(default=False)

    class Meta:
        unique_together = ("job", "freelancer")  # Prevent duplicate applications

    def __str__(self):
        return f"{self.freelancer} applied to {self.job}"


class Review(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="reviews")
    freelancer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews_received"
    )
    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews_given"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (
            "job",
            "freelancer",
        )  # prevent duplicate reviews for same job/freelancer

    def __str__(self):
        return f"Review for {self.freelancer} on {self.job}"
