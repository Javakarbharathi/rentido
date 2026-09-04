from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.users.models import User, UserRole, RoleChoices, RenterProfile, OwnerProfile


class UserAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:token_obtain_pair')
        self.me_url = reverse('users:me')
        self.add_role_url = reverse('users:add_role')

    def test_user_registration_as_renter(self):
        data = {
            "email": "renter@example.com",
            "username": "renter_user",
            "first_name": "Renter",
            "last_name": "Test",
            "phone_number": "+919876543210",
            "password": "Password123!",
            "password_confirm": "Password123!",
            "initial_role": RoleChoices.RENTER
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], "renter@example.com")
        self.assertTrue(User.objects.filter(email="renter@example.com").exists())
        user = User.objects.get(email="renter@example.com")
        self.assertTrue(user.is_renter)
        self.assertTrue(RenterProfile.objects.filter(user=user).exists())

    def test_user_login_and_profile(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="SecurePassword123!"
        )
        UserRole.objects.create(user=user, role=RoleChoices.RENTER, is_active=True)
        RenterProfile.objects.create(user=user)

        # Login
        login_data = {
            "email": "testuser@example.com",
            "password": "SecurePassword123!"
        }
        login_res = self.client.post(self.login_url, login_data)
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_res.data)
        self.assertIn("refresh", login_res.data)
        self.assertEqual(login_res.data["user"]["email"], "testuser@example.com")

        # Access /me with JWT token
        token = login_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        profile_res = self.client.get(self.me_url)
        self.assertEqual(profile_res.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_res.data["username"], "testuser")

    def test_add_owner_role_to_existing_renter(self):
        user = User.objects.create_user(
            email="multi@example.com",
            username="multiuser",
            password="SecurePassword123!"
        )
        UserRole.objects.create(user=user, role=RoleChoices.RENTER, is_active=True)
        RenterProfile.objects.create(user=user)

        self.client.force_authenticate(user=user)
        res = self.client.post(self.add_role_url, {"role": RoleChoices.OWNER})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_owner)
        self.assertTrue(OwnerProfile.objects.filter(user=user).exists())
