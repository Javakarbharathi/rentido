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
from apps.rentals.services.availability import AvailabilityService
from apps.rentals.services.pricing import PricingEngine


class RentalLifecycleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Cameras', slug='cameras')
        
        # 10% commission rule for Cameras
        CommissionRule.objects.create(
            category=self.category,
            commission_type=CommissionRule.CommissionType.PERCENTAGE,
            commission_value=Decimal('10.00'),
            priority=1
        )

        self.owner = User.objects.create_user(
            email='cameraowner@test.com', username='cameraowner', password='Password123!'
        )
        UserRole.objects.create(user=self.owner, role=RoleChoices.OWNER, is_active=True)

        self.renter = User.objects.create_user(
            email='camerarenter@test.com', username='camerarenter', password='Password123!'
        )
        UserRole.objects.create(user=self.renter, role=RoleChoices.RENTER, is_active=True)

        self.asset = Asset.objects.create(
            owner=self.owner,
            category=self.category,
            name='Canon EOS R5',
            brand='Canon',
            model_name='EOS R5',
            serial_number='SN-CANON-001',
            replacement_value=Decimal('250000.00'),
            verification_status=VerificationStatus.VERIFIED,
            status=AssetStatus.AVAILABLE
        )

        self.listing = Listing.objects.create(
            asset=self.asset,
            title='Canon EOS R5 Professional Camera Body',
            description='8K Video & 45MP sensor',
            rental_price=Decimal('2000.00'),
            pricing_model=PricingModel.DAILY,
            security_deposit=Decimal('5000.00'),
            city='Bangalore',
            pincode='560001',
            status=ListingStatus.PUBLISHED
        )

        self.now = timezone.now()
        self.start = self.now + timedelta(days=1)
        self.end = self.now + timedelta(days=3)  # 2 days

    def test_pricing_engine_calculation(self):
        pricing = PricingEngine.calculate_pricing(
            listing=self.listing,
            start_datetime=self.start,
            end_datetime=self.end,
            fulfillment_type=FulfillmentType.DRIVER_DELIVERY
        )

        # 2 days * 2000 = 4000 base
        self.assertEqual(pricing['base_rental_amount'], Decimal('4000.00'))
        # 10% of 4000 = 400 commission
        self.assertEqual(pricing['platform_commission_amount'], Decimal('400.00'))
        # 50 platform fee
        self.assertEqual(pricing['platform_fee'], Decimal('50.00'))
        # 150 delivery fee
        self.assertEqual(pricing['delivery_fee'], Decimal('150.00'))
        # 5000 security deposit
        self.assertEqual(pricing['security_deposit_amount'], Decimal('5000.00'))
        # Total paid: 4000 + 50 + 150 + 5000 = 9200
        self.assertEqual(pricing['total_amount_paid'], Decimal('9200.00'))
        # Owner payout: 4000 - 400 = 3600
        self.assertEqual(pricing['owner_payout_amount'], Decimal('3600.00'))

    def test_availability_service_prevents_double_booking(self):
        # First booking is available
        is_avail, _ = AvailabilityService.check_availability(
            listing=self.listing,
            start_datetime=self.start,
            end_datetime=self.end
        )
        self.assertTrue(is_avail)

        # Create confirmed rental in that interval
        Rental.objects.create(
            renter=self.renter,
            owner=self.owner,
            listing=self.listing,
            start_datetime=self.start,
            end_datetime=self.end,
            status=RentalStatus.CONFIRMED
        )

        # Overlapping check must fail
        overlapping_start = self.now + timedelta(days=2)
        overlapping_end = self.now + timedelta(days=4)
        is_avail_overlap, reason = AvailabilityService.check_availability(
            listing=self.listing,
            start_datetime=overlapping_start,
            end_datetime=overlapping_end
        )
        self.assertFalse(is_avail_overlap)
        self.assertIn("already reserved", reason)

    def test_full_rental_booking_and_lifecycle_flow(self):
        self.client.force_authenticate(user=self.renter)
        book_url = reverse('rentals:rental-book')

        data = {
            'listing_id': self.listing.id,
            'start_datetime': self.start.isoformat(),
            'end_datetime': self.end.isoformat(),
            'fulfillment_type': FulfillmentType.SELF_PICKUP
        }
        res = self.client.post(book_url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        rental_id = res.data['id']
        self.assertEqual(res.data['status'], RentalStatus.PAYMENT_PENDING)
        self.assertTrue('pricing_snapshot' in res.data)
        self.assertEqual(res.data['pricing_snapshot']['base_rental_amount'], '4000.00')

        # 1. Confirm Payment
        confirm_url = reverse('rentals:rental-confirm-payment', kwargs={'pk': rental_id})
        res_confirm = self.client.post(confirm_url)
        self.assertEqual(res_confirm.status_code, status.HTTP_200_OK)
        self.assertEqual(res_confirm.data['status'], RentalStatus.CONFIRMED)

        rental = Rental.objects.get(id=rental_id)

        # 2. Handover via Handover OTP
        handover_url = reverse('rentals:rental-handover', kwargs={'pk': rental_id})
        res_handover = self.client.post(handover_url, {'otp': rental.handover_otp})
        self.assertEqual(res_handover.status_code, status.HTTP_200_OK)
        self.assertEqual(res_handover.data['status'], RentalStatus.ACTIVE)

        # 3. Renter Requests Return
        return_req_url = reverse('rentals:rental-request-return', kwargs={'pk': rental_id})
        res_return_req = self.client.post(return_req_url)
        self.assertEqual(res_return_req.status_code, status.HTTP_200_OK)
        self.assertEqual(res_return_req.data['status'], RentalStatus.RETURN_REQUESTED)

        # 4. Complete Return via Return OTP
        return_url = reverse('rentals:rental-return-asset', kwargs={'pk': rental_id})
        res_return = self.client.post(return_url, {'otp': rental.return_otp})
        self.assertEqual(res_return.status_code, status.HTTP_200_OK)
        self.assertEqual(res_return.data['status'], RentalStatus.COMPLETED)

    def test_rental_extension_lifecycle_and_addendum(self):
        # 1. Create Active Rental
        rental = Rental.objects.create(
            renter=self.renter, owner=self.owner, listing=self.listing,
            start_datetime=self.start, end_datetime=self.end,
            fulfillment_type=FulfillmentType.SELF_PICKUP,
            status=RentalStatus.ACTIVE
        )

        # 2. Renter requests 1-day extension
        self.client.force_authenticate(user=self.renter)
        ext_req_url = reverse('rentals:rental-request-extension', kwargs={'pk': rental.id})
        new_end = self.end + timedelta(days=1)
        res_req = self.client.post(ext_req_url, {'new_end_datetime': new_end.isoformat(), 'reason': 'Shoot rescheduled'})
        self.assertEqual(res_req.status_code, status.HTTP_201_CREATED)
        ext_id = res_req.data['id']
        rental.refresh_from_db()
        self.assertEqual(rental.status, RentalStatus.EXTENSION_PENDING)

        # 3. Owner approves extension
        self.client.force_authenticate(user=self.owner)
        decide_url = reverse('rentals:extension-decide', kwargs={'pk': ext_id})
        res_decide = self.client.post(decide_url, {'approve': True})
        self.assertEqual(res_decide.status_code, status.HTTP_200_OK)

        # 4. Renter pays for extension
        self.client.force_authenticate(user=self.renter)
        pay_url = reverse('rentals:extension-pay-extension', kwargs={'pk': ext_id})
        res_pay = self.client.post(pay_url, {'payment_method': 'UPI'})
        self.assertEqual(res_pay.status_code, status.HTTP_200_OK)
        self.assertTrue(res_pay.data['is_paid'])

        rental.refresh_from_db()
        self.assertEqual(rental.status, RentalStatus.ACTIVE)
        self.assertEqual(rental.end_datetime, new_end)
        self.assertTrue(hasattr(rental, 'agreement'))
        self.assertEqual(rental.agreement.addendums.count(), 1)

