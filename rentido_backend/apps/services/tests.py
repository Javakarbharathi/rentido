from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.categories.models import Category
from apps.assets.models import Asset, VerificationStatus, AssetStatus
from apps.users.models import User, RoleChoices, UserRole
from apps.services.models import (
    ServiceProvider,
    ServiceRequest,
    ServiceCategory,
    ServiceRequestStatus,
    ServiceCommissionRule,
)


class ServicesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Cameras', slug='cameras')
        self.owner = User.objects.create_user(
            email='srvowner@test.com', username='srvowner', password='Password123!'
        )
        UserRole.objects.create(user=self.owner, role=RoleChoices.OWNER, is_active=True)

        self.provider_user = User.objects.create_user(
            email='technician@test.com', username='technician', password='Password123!'
        )

        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'AdminPass123!')

        self.asset = Asset.objects.create(
            owner=self.owner, category=self.category,
            name='Sony FX3 Cinema Camera', brand='Sony', model_name='FX3',
            serial_number='SN-SONY-FX3-99', replacement_value=Decimal('350000.00'),
            verification_status=VerificationStatus.VERIFIED, status=AssetStatus.AVAILABLE
        )

        ServiceCommissionRule.objects.create(
            category=ServiceCategory.CAMERA_REPAIR,
            commission_percentage=Decimal('10.00')
        )

    def test_service_provider_registration_auto_assigns_role(self):
        self.client.force_authenticate(user=self.provider_user)
        url = reverse('services:provider-list')
        data = {
            'category': ServiceCategory.CAMERA_REPAIR,
            'business_name': 'Pro Camera Doctor',
            'phone_number': '+919988776655',
            'address': '101 Tech Street',
            'city': 'Chennai',
            'pincode': '600002',
            'experience_years': 8,
            'base_diagnostic_fee': '300.00'
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.provider_user.refresh_from_db()
        self.assertTrue(self.provider_user.is_service_provider)
        self.assertTrue(ServiceProvider.objects.filter(business_name='Pro Camera Doctor').exists())

    def test_full_repair_request_quote_and_closure_flow(self):
        # 1. Register and verify provider
        provider = ServiceProvider.objects.create(
            user=self.provider_user, category=ServiceCategory.CAMERA_REPAIR,
            business_name='Pro Camera Doctor', phone_number='+919988776655',
            address='101 Tech Street', city='Chennai', pincode='600002',
            is_verified=True, is_available=True
        )

        # 2. Asset owner requests repair
        self.client.force_authenticate(user=self.owner)
        url = reverse('services:repair-request-list')
        data = {
            'asset': self.asset.id,
            'assigned_provider': provider.id,
            'category': ServiceCategory.CAMERA_REPAIR,
            'issue_title': 'Sensor Dust Cleaning & Fan Issue',
            'description': 'Fan making buzzing noise and spots on sensor'
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        job_id = res.data['id']

        # 3. Provider submits quote
        self.client.force_authenticate(user=self.provider_user)
        quote_url = reverse('services:repair-request-submit-quote', kwargs={'pk': job_id})
        res_quote = self.client.post(quote_url, {
            'final_quote_amount': '2000.00',
            'quote_notes': 'Includes sensor swab, cleaning solution, and fan realignment'
        })
        self.assertEqual(res_quote.status_code, status.HTTP_200_OK)
        self.assertEqual(res_quote.data['platform_commission'], '200.00')
        self.assertEqual(res_quote.data['provider_payout'], '1800.00')

        # 4. Owner approves quote -> asset placed into MAINTENANCE
        self.client.force_authenticate(user=self.owner)
        approve_url = reverse('services:repair-request-approve-quote', kwargs={'pk': job_id})
        res_appr = self.client.post(approve_url, {'payment_method': 'UPI'})
        self.assertEqual(res_appr.status_code, status.HTTP_200_OK)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, AssetStatus.MAINTENANCE)

        # 5. Provider completes repair
        self.client.force_authenticate(user=self.provider_user)
        done_url = reverse('services:repair-request-complete-repair', kwargs={'pk': job_id})
        res_done = self.client.post(done_url)
        self.assertEqual(res_done.status_code, status.HTTP_200_OK)
        self.assertEqual(res_done.data['status'], ServiceRequestStatus.REPAIRED)

        # 6. Owner/Admin inspects and closes -> asset restored to AVAILABLE
        self.client.force_authenticate(user=self.owner)
        close_url = reverse('services:repair-request-inspect-and-close', kwargs={'pk': job_id})
        res_close = self.client.post(close_url)
        self.assertEqual(res_close.status_code, status.HTTP_200_OK)
        self.assertEqual(res_close.data['status'], ServiceRequestStatus.INSPECTED_CLOSED)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, AssetStatus.AVAILABLE)
