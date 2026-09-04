from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, RoleChoices, UserRole
from apps.categories.models import Category
from apps.assets.models import Asset
from apps.listings.models import Listing, PricingModel, ListingStatus
from apps.rentals.models import Rental, RentalStatus
from apps.rentals.services.pricing import PricingEngine
from apps.promotions.models import (
    Coupon,
    DiscountType,
    SurgePricingRule,
    ReferralCode,
    ReferralReward,
)
from apps.promotions.services.promotions import PromotionService
from apps.trust.models import TrustProfile, TrustEventType


class PromotionsAndPricingTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='promo_owner',
            email='promo_owner@rentido.com',
            password='password123'
        )
        UserRole.objects.create(user=self.owner, role=RoleChoices.OWNER, is_active=True)

        self.renter = User.objects.create_user(
            username='promo_renter',
            email='promo_renter@rentido.com',
            password='password123'
        )
        UserRole.objects.create(user=self.renter, role=RoleChoices.RENTER, is_active=True)

        self.category = Category.objects.create(name='Audio & Studio', slug='audio')
        self.asset = Asset.objects.create(
            owner=self.owner,
            category=self.category,
            name='Shure SM7B Studio Mic Kit',
            serial_number='SHURE-SM7B-001',
            replacement_value=Decimal('45000.00')
        )
        self.listing = Listing.objects.create(
            asset=self.asset,
            title='Shure SM7B Vocal Microphone',
            description='Studio recording dynamic microphone',
            rental_price=Decimal('1000.00'),
            pricing_model=PricingModel.DAILY,
            security_deposit=Decimal('4000.00'),
            city='Bangalore',
            pincode='560001',
            status=ListingStatus.PUBLISHED
        )

        self.now = timezone.now()
        self.start = self.now + timedelta(days=1)
        self.end = self.now + timedelta(days=3)  # 2 days -> ₹2000

    def test_percentage_coupon_with_cap(self):
        """20% coupon capped at 300 discount on ₹2000 rental yields ₹300 discount."""
        coupon = Coupon.objects.create(
            code='SAVE20',
            title='20% Off Promo',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal('20.00'),
            max_discount_amount=Decimal('300.00'),
            minimum_rental_amount=Decimal('500.00'),
            is_active=True
        )

        pricing = PricingEngine.calculate_pricing(
            listing=self.listing,
            start_datetime=self.start,
            end_datetime=self.end,
            user=self.renter,
            coupon_code='SAVE20'
        )
        self.assertEqual(pricing['base_rental_amount'], Decimal('2000.00'))
        self.assertEqual(pricing['discount_amount'], Decimal('300.00'))
        self.assertEqual(pricing['coupon_code'], 'SAVE20')
        # Total = (2000 - 300) + 50 (platform) + 0 (pickup) + 4000 (deposit) = 5750
        self.assertEqual(pricing['total_amount_paid'], Decimal('5750.00'))

    def test_flat_discount_and_minimum_order(self):
        """Flat ₹500 discount requires minimum ₹2500 base rent."""
        coupon = Coupon.objects.create(
            code='FLAT500',
            title='Flat 500 Off',
            discount_type=DiscountType.FLAT,
            discount_value=Decimal('500.00'),
            minimum_rental_amount=Decimal('2500.00'),
            is_active=True
        )

        # 1. Rental of 2 days = ₹2000 (below min ₹2500)
        pricing_fail = PricingEngine.calculate_pricing(
            listing=self.listing,
            start_datetime=self.start,
            end_datetime=self.end,
            coupon_code='FLAT500'
        )
        self.assertEqual(pricing_fail['discount_amount'], Decimal('0.00'))

        # 2. Rental of 3 days = ₹3000 (exceeds min ₹2500)
        end_3_days = self.now + timedelta(days=4)
        pricing_ok = PricingEngine.calculate_pricing(
            listing=self.listing,
            start_datetime=self.start,
            end_datetime=end_3_days,
            coupon_code='FLAT500'
        )
        self.assertEqual(pricing_ok['discount_amount'], Decimal('500.00'))

    def test_coupon_validate_api_endpoint(self):
        """Test /api/promotions/coupons/validate/ endpoint."""
        Coupon.objects.create(
            code='WELCOME10',
            title='Welcome 10% Discount',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal('10.00'),
            is_active=True
        )

        payload = {
            'code': 'WELCOME10',
            'listing_id': self.listing.id,
            'start_datetime': self.start.isoformat(),
            'end_datetime': self.end.isoformat()
        }
        response = self.client.post('/api/coupons/validate/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])
        self.assertEqual(Decimal(str(response.data['discount_amount'])), Decimal('200.00'))

    def test_surge_pricing_multiplier(self):
        """Surge rule applies 1.25x multiplier to base rental price."""
        SurgePricingRule.objects.create(
            name='Weekend Studio Rush',
            city='Bangalore',
            category=self.category,
            multiplier=Decimal('1.25'),
            start_datetime=self.now - timedelta(days=1),
            end_datetime=self.now + timedelta(days=5),
            is_active=True
        )

        pricing = PricingEngine.calculate_pricing(
            listing=self.listing,
            start_datetime=self.start,
            end_datetime=self.end
        )
        # 2 days * 1000 * 1.25 = 2500.00
        self.assertEqual(pricing['surge_multiplier'], Decimal('1.25'))
        self.assertEqual(pricing['base_rental_amount'], Decimal('2500.00'))

    def test_referral_lifecycle(self):
        """User A gets code, User B claims it, completing rental rewards User A."""
        # 1. User A generates / retrieves referral code
        self.client.force_authenticate(user=self.owner)
        me_resp = self.client.get('/api/referrals/me/')
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        code = me_resp.data['referral_code']
        self.assertTrue(len(code) > 0)

        # 2. User B claims User A's referral code
        self.client.force_authenticate(user=self.renter)
        claim_resp = self.client.post('/api/referrals/claim/', {'referral_code': code})
        self.assertEqual(claim_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(claim_resp.data['status'], 'SUCCESS')

        # 3. Completing first rental awards referral points to User A
        owner_profile, _ = TrustProfile.objects.get_or_create(user=self.owner)
        initial_score = owner_profile.trust_score

        PromotionService.process_referral_completion(referee=self.renter)
        owner_profile.refresh_from_db()
        self.assertEqual(owner_profile.trust_score, initial_score + 25)
