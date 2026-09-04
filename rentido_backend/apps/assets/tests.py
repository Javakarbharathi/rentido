from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.categories.models import Category
from apps.assets.models import Asset, VerificationStatus, AssetStatus, AssetCondition
from apps.users.models import User, RoleChoices, UserRole


class AssetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.owner = User.objects.create_user(
            email='owner@test.com', username='owner', password='Password123!'
        )
        UserRole.objects.create(user=self.owner, role=RoleChoices.OWNER, is_active=True)
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'AdminPass123!')

    def test_owner_can_register_asset(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('assets:asset-list')
        data = {
            'category': self.category.id,
            'name': 'Sony A7 IV',
            'brand': 'Sony',
            'model_name': 'Alpha 7 IV',
            'serial_number': 'SN-SONY-9988',
            'condition': AssetCondition.LIKE_NEW,
            'replacement_value': '180000.00',
            'notes': 'Includes 28-70mm kit lens'
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Asset.objects.filter(serial_number='SN-SONY-9988').exists())
        asset = Asset.objects.get(serial_number='SN-SONY-9988')
        self.assertEqual(asset.owner, self.owner)
        self.assertEqual(asset.verification_status, VerificationStatus.PENDING)

    def test_admin_can_verify_asset(self):
        asset = Asset.objects.create(
            owner=self.owner,
            category=self.category,
            name='Drone Mavic 3',
            brand='DJI',
            model_name='Mavic 3 Pro',
            serial_number='SN-DJI-4455',
            replacement_value='150000.00'
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('assets:asset-verify', kwargs={'pk': asset.id})
        data = {
            'verification_status': VerificationStatus.VERIFIED,
            'notes': 'Ownership invoice checked and verified'
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        asset.refresh_from_db()
        self.assertEqual(asset.verification_status, VerificationStatus.VERIFIED)
        self.assertEqual(asset.status, AssetStatus.AVAILABLE)
