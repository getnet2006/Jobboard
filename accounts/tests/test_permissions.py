from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class PermissionTestCase(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client", password="clientpass123", role="client"
        )
        self.freelancer_user = User.objects.create_user(
            username="freelancer",
            password="freelancerpass123",
            role="freelancer",
        )

        self.client_token = get_token_for_user(self.client_user)
        self.freelancer_token = get_token_for_user(self.freelancer_user)

        # Dummy endpoint for testing (update with your actual view name)
        self.protected_url = reverse("job-list-create")  # e.g., JobCreateView

    def test_client_can_access_client_view(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.client_token}")
        response = self.client.get(self.protected_url)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_freelancer_cannot_access_client_view(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.freelancer_token}")
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access(self):
        self.client.credentials()
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
