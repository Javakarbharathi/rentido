from datetime import timedelta
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.categories.models import Category
from apps.assets.models import Asset, VerificationStatus, AssetStatus
from apps.listings.models import Listing, PricingModel, ListingStatus
from apps.users.models import User, RoleChoices, UserRole
from apps.rentals.models import Rental, RentalStatus, FulfillmentType, RentalPricingSnapshot
from apps.payments.models import SecurityDeposit, DepositStatus
from apps.inspections.models import (
    Inspection,
    InspectionType,
    ConditionGrade,
    DamageReport,
    DamageSeverity,
    DamageResponsibility,
    DamageStatus,
)


class InspectionAndDamageTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Audio', slug='audio')
        self.owner = User.objects.create_user(
            email='inspowner@test.com', username='inspowner', password='Password123!'
        )
        UserRole.objects.create(user=self.owner, role=RoleChoices.OWNER, is_active=True)

        self.renter = User.objects.create_user(
            email='insprenter@test.com', username='insprenter', password='Password123!'
        )
        UserRole.objects.create(user=self.renter, role=RoleChoices.RENTER, is_active=True)

        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'AdminPass123!')

        self.asset = Asset.objects.create(
            owner=self.owner, category=self.category,
            name='Wireless Mic Kit', brand='Rode', model_name='Wireless GO II',
            serial_number='SN-RODE-111', replacement_value=Decimal('25000.00'),
            verification_status=VerificationStatus.VERIFIED, status=AssetStatus.AVAILABLE
        )

        self.listing = Listing.objects.create(
            asset=self.asset, title='Rode Wireless GO II Dual', description='Crystal clear audio',
            rental_price=Decimal('500.00'), pricing_model=PricingModel.DAILY,
            security_deposit=Decimal('2000.00'), city='Chennai', pincode='600001',
            status=ListingStatus.PUBLISHED
        )

        now = timezone.now()
        self.rental = Rental.objects.create(
            renter=self.renter, owner=self.owner, listing=self.listing,
            start_datetime=now + timedelta(days=1),
            end_datetime=now + timedelta(days=2),
            fulfillment_type=FulfillmentType.SELF_PICKUP,
            status=RentalStatus.ACTIVE
        )

        RentalPricingSnapshot.objects.create(
            rental=self.rental, base_rental_amount=Decimal('500.00'),
            platform_commission_rate=Decimal('10.00'),
            platform_commission_amount=Decimal('50.00'),
            platform_fee=Decimal('50.00'), delivery_fee=Decimal('0.00'),
            security_deposit_amount=Decimal('2000.00'),
            total_amount_paid=Decimal('2550.00'),
            owner_payout_amount=Decimal('450.00')
        )

        SecurityDeposit.objects.create(
            rental=self.rental, renter=self.renter,
            total_amount=Decimal('2000.00'), status=DepositStatus.HELD
        )

    def test_submit_inspection(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('inspections:inspection-list')
        data = {
            'rental': self.rental.id,
            'inspection_type': InspectionType.RETURN,
            'condition_grade': ConditionGrade.DAMAGED,
            'checklist_answers': {'powers_on': True, 'mic_clip_broken': True},
            'notes': 'Mic transmitter clip is broken'
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Inspection.objects.filter(rental=self.rental).exists())

    def test_damage_report_and_admin_settlement(self):
        # 1. Owner files damage report
        self.client.force_authenticate(user=self.owner)
        url = reverse('inspections:damage-report-list')
        data = {
            'rental': self.rental.id,
            'description': 'Lavalier cable torn during use',
            'severity': DamageSeverity.MEDIUM,
            'estimated_repair_cost': '1200.00'
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        report_id = res.data['id']

        # 2. Admin resolves report & approves deduction of 1000 from security deposit
        self.client.force_authenticate(user=self.admin)
        resolve_url = reverse('inspections:damage-report-resolve', kwargs={'pk': report_id})
        resolve_data = {
            'responsibility': DamageResponsibility.RENTER_RESPONSIBILITY,
            'approved_deduction_amount': '1000.00',
            'resolution_notes': 'Deducting replacement cost of lavalier cable from held deposit'
        }
        res_resolve = self.client.post(resolve_url, resolve_data)
        self.assertEqual(res_resolve.status_code, status.HTTP_200_OK)
        self.assertEqual(res_resolve.data['status'], DamageStatus.SETTLED)

        # 3. Verify security deposit was partially deducted in database
        deposit = SecurityDeposit.objects.get(rental=self.rental)
        self.assertEqual(deposit.status, DepositStatus.PARTIALLY_DEDUCTED)
        self.assertEqual(deposit.deducted_amount, Decimal('1000.00'))
        self.assertEqual(deposit.refunded_amount, Decimal('1000.00'))
