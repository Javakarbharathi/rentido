from datetime import timedelta
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.categories.models import Category, CommissionRule
from apps.assets.models import Asset, VerificationStatus, AssetStatus
from apps.listings.models import Listing, PricingModel, ListingStatus
from apps.users.models import User, RoleChoices, UserRole
from apps.rentals.models import Rental, RentalStatus, FulfillmentType
from apps.rentals.services.pricing import PricingEngine
from apps.payments.models import (
    Payment,
    PaymentStatus,
    SecurityDeposit,
    DepositStatus,
    LedgerEntry,
    LedgerEntryType,
    LedgerAccount,
)
from apps.payments.services.ledger import LedgerService


class PaymentAndLedgerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        CommissionRule.objects.create(
            category=self.category,
            commission_type=CommissionRule.CommissionType.PERCENTAGE,
            commission_value=Decimal('10.00'),
            priority=1
        )
        self.owner = User.objects.create_user(
            email='payowner@test.com', username='payowner', password='Password123!'
        )
        UserRole.objects.create(user=self.owner, role=RoleChoices.OWNER, is_active=True)

        self.renter = User.objects.create_user(
            email='payrenter@test.com', username='payrenter', password='Password123!'
        )
        UserRole.objects.create(user=self.renter, role=RoleChoices.RENTER, is_active=True)

        self.asset = Asset.objects.create(
            owner=self.owner, category=self.category,
            name='Projector 4K', brand='Epson', model_name='Home Cinema 4K',
            serial_number='SN-PROJ-99', replacement_value=Decimal('80000.00'),
            verification_status=VerificationStatus.VERIFIED, status=AssetStatus.AVAILABLE
        )

        self.listing = Listing.objects.create(
            asset=self.asset, title='4K Cinema Projector', description='Super bright',
            rental_price=Decimal('1000.00'), pricing_model=PricingModel.DAILY,
            security_deposit=Decimal('2000.00'), city='Bangalore', pincode='560001',
            status=ListingStatus.PUBLISHED
        )

        now = timezone.now()
        start = now + timedelta(days=1)
        end = now + timedelta(days=3)  # 2 days = 2000 rental

        self.rental = Rental.objects.create(
            renter=self.renter, owner=self.owner, listing=self.listing,
            start_datetime=start, end_datetime=end,
            fulfillment_type=FulfillmentType.SELF_PICKUP,
            status=RentalStatus.PAYMENT_PENDING
        )

        pricing = PricingEngine.calculate_pricing(self.listing, start, end, FulfillmentType.SELF_PICKUP)
        from apps.rentals.models import RentalPricingSnapshot
        RentalPricingSnapshot.objects.create(
            rental=self.rental,
            base_rental_amount=pricing['base_rental_amount'],
            platform_commission_rate=pricing['platform_commission_rate'],
            platform_commission_amount=pricing['platform_commission_amount'],
            platform_fee=pricing['platform_fee'],
            delivery_fee=pricing['delivery_fee'],
            security_deposit_amount=pricing['security_deposit_amount'],
            total_amount_paid=pricing['total_amount_paid'],
            owner_payout_amount=pricing['owner_payout_amount'],
            raw_calculation=pricing['raw_calculation']
        )

    def test_payment_processing_creates_ledger_and_confirms_rental(self):
        self.client.force_authenticate(user=self.renter)
        url = reverse('payments:payment-process-payment')
        data = {'rental_id': self.rental.id, 'payment_method': 'UPI'}

        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], PaymentStatus.SUCCESS)

        self.rental.refresh_from_db()
        self.assertEqual(self.rental.status, RentalStatus.CONFIRMED)

        # Verify SecurityDeposit record was created in HELD status
        deposit = SecurityDeposit.objects.get(rental=self.rental)
        self.assertEqual(deposit.total_amount, Decimal('2000.00'))
        self.assertEqual(deposit.status, DepositStatus.HELD)

        # Verify Ledger Entries exist
        entries = LedgerEntry.objects.filter(rental=self.rental)
        # Inflow, Deposit Held, Commission, Platform Fee, Owner Payable
        self.assertTrue(entries.filter(entry_type=LedgerEntryType.SECURITY_DEPOSIT_HELD).exists())
        self.assertTrue(entries.filter(entry_type=LedgerEntryType.PLATFORM_COMMISSION_EARNED).exists())
        self.assertTrue(entries.filter(entry_type=LedgerEntryType.OWNER_PAYABLE_CREDITED).exists())

    def test_security_deposit_partial_deduction_and_release(self):
        # 1. Simulate initial payment
        payment = Payment.objects.create(
            rental=self.rental, payer=self.renter, amount=Decimal('4050.00'),
            transaction_id='TXN-TEST-123', status=PaymentStatus.SUCCESS
        )
        LedgerService.record_rental_payment(self.rental, payment)

        # 2. Settle deposit with damage deduction of 500 (refund 1500 to renter)
        deposit = LedgerService.settle_security_deposit(
            rental=self.rental,
            deduction_amount=Decimal('500.00'),
            reason="Scratch on lens cap"
        )
        self.assertEqual(deposit.status, DepositStatus.PARTIALLY_DEDUCTED)
        self.assertEqual(deposit.deducted_amount, Decimal('500.00'))
        self.assertEqual(deposit.refunded_amount, Decimal('1500.00'))

        # Verify ledger entries for deduction and release
        self.assertTrue(LedgerEntry.objects.filter(
            rental=self.rental, entry_type=LedgerEntryType.DEPOSIT_DEDUCTED
        ).exists())
        self.assertTrue(LedgerEntry.objects.filter(
            rental=self.rental, entry_type=LedgerEntryType.DEPOSIT_RELEASED
        ).exists())
