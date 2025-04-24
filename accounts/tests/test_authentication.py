from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class JWTAuthTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", role="client"
        )

    def test_token_obtain(self):
        url = reverse("token_obtain_pair")  # Use your custom JWT view name
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
