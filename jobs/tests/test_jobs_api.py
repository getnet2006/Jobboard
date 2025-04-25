from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from jobs.models import Application, Job


class JobTests(APITestCase):

    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client", password="TestPass123!", role="client"
        )
        self.token = str(RefreshToken.for_user(self.client_user).access_token)
        self.auth_header = f"Bearer {self.token}"
        self.create_url = reverse("job-list-create")

    def test_client_can_create_job(self):
        job_data = {
            "title": "Test Job",
            "description": "This is a test job.",
            "budget": 500,
            "max_applicants": 3,
        }

        response = self.client.post(
            self.create_url,
            job_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth_header,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Job.objects.count(), 1)
        self.assertEqual(Job.objects.first().title, "Test Job")

    def test_client_can_view_job_list(self):
        job_data = {
            "title": "Test Job",
            "description": "This is a test job.",
            "budget": 500,
            "max_applicants": 3,
        }

        self.client.post(
            self.create_url,
            job_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth_header,
        )

        response = self.client.get(self.create_url, HTTP_AUTHORIZATION=self.auth_header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Job")

    def test_client_can_view_job_detail(self):
        job_data = {
            "title": "Test Job",
            "description": "This is a test job.",
            "budget": 500,
            "max_applicants": 3,
        }

        job_response = self.client.post(
            self.create_url,
            job_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth_header,
        )

        job_id = job_response.data["id"]
        detail_url = reverse("job-detail", args=[job_id])

        response = self.client.get(detail_url, HTTP_AUTHORIZATION=self.auth_header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Job")

    def test_freelancer_cannot_create_job(self):
        freelancer = User.objects.create_user(
            username="freelancer@example.com",
            password="Freelance123!",
            role="freelancer",
        )
        token = str(RefreshToken.for_user(freelancer).access_token)

        response = self.client.post(
            self.create_url,
            {
                "title": "Freelancer Post",
                "description": "Should not be allowed.",
                "budget": 100,
                "max_applications": 3,
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_can_update_own_job(self):
        job = Job.objects.create(
            client=self.client_user,
            title="Old Title",
            description="Old Description",
            budget=200,
        )

        url = reverse("job-detail", args=[job.id])

        response = self.client.put(
            url,
            {"title": "New Title", "description": "Updated Description", "budget": 300},
            format="json",
            HTTP_AUTHORIZATION=self.auth_header,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        job.refresh_from_db()
        self.assertEqual(job.title, "New Title")

    def test_other_client_cannot_update_job(self):
        other_client = User.objects.create_user(
            username="otherclient", password="Client456!", role="client"
        )
        job = Job.objects.create(
            client=self.client_user,
            title="Private Job",
            description="Shouldn't be editable.",
            budget=100,
        )

        url = reverse("job-detail", args=[job.id])
        token = str(RefreshToken.for_user(other_client).access_token)

        response = self.client.put(
            url,
            {"title": "Hacked Title", "description": "Nope.", "budget": 999},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_freelancer_can_apply_to_job(self):
        freelancer = User.objects.create_user(
            username="freelancer1", password="Test1234!", role="freelancer"
        )
        job = Job.objects.create(
            client=self.client_user,
            title="Design Logo",
            description="Need a logo designer.",
            budget=300,
        )
        token = str(RefreshToken.for_user(freelancer).access_token)

        apply_url = reverse("apply-to-job")

        response = self.client.post(
            apply_url,
            {"job": job.id, "cover_letter": "I can do this job!"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(job.applications.count(), 1)

    def test_freelancer_cannot_apply_twice(self):
        freelancer = User.objects.create_user(
            username="freelancer2", password="Test1234!", role="freelancer"
        )
        job = Job.objects.create(
            client=self.client_user,
            title="Build Website",
            description="Need a frontend dev.",
            budget=500,
        )
        Application = job.applications.model
        Application.objects.create(
            job=job, freelancer=freelancer, cover_letter="First try"
        )

        token = str(RefreshToken.for_user(freelancer).access_token)
        apply_url = reverse("apply-to-job")

        response = self.client.post(
            apply_url,
            {"job": job.id, "cover_letter": "Second try"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)

    def test_client_cannot_apply_to_job(self):
        job = Job.objects.create(
            client=self.client_user,
            title="Editing Help",
            description="Need an editor",
            budget=150,
        )

        apply_url = reverse("apply-to-job")

        response = self.client.post(
            apply_url,
            {"job": job.id, "cover_letter": "I'm a client but trying to apply"},
            format="json",
            HTTP_AUTHORIZATION=self.auth_header,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_freelancer_can_view_applied_jobs(self):
        freelancer = User.objects.create_user(
            username="freelancer3", password="Test1234!", role="freelancer"
        )
        job1 = Job.objects.create(
            client=self.client_user, title="Job 1", description="...", budget=100
        )
        job2 = Job.objects.create(
            client=self.client_user, title="Job 2", description="...", budget=200
        )
        Application.objects.create(job=job1, freelancer=freelancer, cover_letter="Hi 1")
        Application.objects.create(job=job2, freelancer=freelancer, cover_letter="Hi 2")

        token = str(RefreshToken.for_user(freelancer).access_token)
        url = reverse("job-applications")

        response = self.client.get(
            url, format="json", HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["job"]["title"], "Job 2")

    def test_max_applications_limit_enforced(self):
        job = Job.objects.create(
            client=self.client_user,
            title="Limited Job",
            description="Only 2 applicants allowed.",
            budget=100,
            max_applications=2,
        )

        # Create and apply two freelancers
        for i in range(2):
            user = User.objects.create_user(
                username=f"freelancer{i}", password="Test123!", role="freelancer"
            )
            Application.objects.create(job=job, freelancer=user, cover_letter="I'm in.")

        # A third freelancer tries to apply
        new_freelancer = User.objects.create_user(
            username="freelancer3", password="Test123!", role="freelancer"
        )
        token = str(RefreshToken.for_user(new_freelancer).access_token)
        apply_url = reverse("apply-to-job")

        response = self.client.post(
            apply_url,
            {"job": job.id, "cover_letter": "Too late?"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(
        #     response.data.get("message"), "Maximum number of applicants reached."
        # )

    def test_client_can_hire_freelancer(self):
        freelancer = User.objects.create_user(
            username="freelancer4@example.com",
            password="Test1234!",
            role="freelancer"
        )
        job = Job.objects.create(client=self.client_user, title="Hire Test", description="...", budget=250)
        application = Application.objects.create(job=job, freelancer=freelancer, cover_letter="Hire me!")

        token = str(RefreshToken.for_user(self.client_user).access_token)
        url = reverse("application-hire", args=[application.id])  # Custom action

        response = self.client.post(
            url,
            {},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        application.refresh_from_db()
        self.assertTrue(application.is_hired)
