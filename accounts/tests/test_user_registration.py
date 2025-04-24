from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from accounts.models import User


class UserRegistrationTest(APITestCase):
    def test_register_freelancer(self):
        url = reverse("register")
        data = {
            "username": "freelancer_user",
            "first_name": "Freelancer",
            "last_name": "User",
            "email": "freelancer@example.com",
            "password": "StrongPass123!",
            "role": "freelancer",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().role, "freelancer")
