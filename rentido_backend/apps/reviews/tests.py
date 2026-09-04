from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, RoleChoices, UserRole
from apps.categories.models import Category
from apps.assets.models import Asset
from apps.listings.models import Listing, PricingModel, ListingStatus
from apps.rentals.models import Rental, RentalStatus
from apps.reviews.models import Review, ReviewTargetType
from apps.trust.models import TrustProfile, TrustEventType


class ReviewEngineTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@rentido.com',
            password='password123',
            first_name='Asset',
            last_name='Owner'
        )
        UserRole.objects.create(user=self.owner, role=RoleChoices.OWNER, is_active=True)

        self.renter = User.objects.create_user(
            username='renter',
            email='renter@rentido.com',
            password='password123',
            first_name='Good',
            last_name='Renter'
        )
        UserRole.objects.create(user=self.renter, role=RoleChoices.RENTER, is_active=True)

        self.other_user = User.objects.create_user(
            username='other',
            email='other@rentido.com',
            password='password123',
            first_name='Random',
            last_name='User'
        )
        UserRole.objects.create(user=self.other_user, role=RoleChoices.RENTER, is_active=True)

        self.category = Category.objects.create(name='Cameras & Optics', slug='cameras')
        self.asset = Asset.objects.create(
            owner=self.owner,
            category=self.category,
            name='Canon EOS R5',
            serial_number='CANON-R5-9988',
            replacement_value=Decimal('250000.00')
        )
        self.listing = Listing.objects.create(
            asset=self.asset,
            title='Canon R5 8K Mirrorless Kit',
            description='Professional camera kit',
            rental_price=Decimal('1500.00'),
            pricing_model=PricingModel.DAILY,
            security_deposit=Decimal('10000.00'),
            city='Bangalore',
            pincode='560001',
            status=ListingStatus.PUBLISHED
        )

        now = timezone.now()
        self.rental = Rental.objects.create(
            renter=self.renter,
            owner=self.owner,
            listing=self.listing,
            start_datetime=now - timedelta(days=3),
            end_datetime=now - timedelta(days=1),
            status=RentalStatus.ACTIVE
        )

    def test_cannot_review_active_rental(self):
        """Reviews can only be submitted after rental is COMPLETED."""
        self.client.force_authenticate(user=self.renter)
        data = {
            'rental_id': self.rental.id,
            'target_type': ReviewTargetType.OWNER,
            'rating': 5,
            'comment': 'Awesome camera, very clean handover!'
        }
        response = self.client.post('/api/reviews/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Reviews can only be submitted after the rental is COMPLETED", str(response.data))

    def test_renter_reviews_owner_and_asset_after_completion(self):
        """Completed rental allows renter to review owner and asset, adjusting trust score."""
        self.rental.status = RentalStatus.COMPLETED
        self.rental.save()

        # Initial owner trust score
        owner_profile, _ = TrustProfile.objects.get_or_create(user=self.owner)
        initial_score = owner_profile.trust_score

        self.client.force_authenticate(user=self.renter)

        # 1. Review owner with 5 stars
        owner_review_data = {
            'rental_id': self.rental.id,
            'target_type': ReviewTargetType.OWNER,
            'rating': 5,
            'comment': 'Exceptional host! Smooth handover.'
        }
        response = self.client.post('/api/reviews/', owner_review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

        # Verify owner trust score increased by 15
        owner_profile.refresh_from_db()
        self.assertEqual(owner_profile.trust_score, initial_score + 15)
        self.assertTrue(owner_profile.events.filter(event_type=TrustEventType.POSITIVE_REVIEW).exists())

        # 2. Review physical asset with 4 stars
        asset_review_data = {
            'rental_id': self.rental.id,
            'target_type': ReviewTargetType.ASSET,
            'rating': 4,
            'comment': 'Sensor was pristine, battery was at 100%.'
        }
        response2 = self.client.post('/api/reviews/', asset_review_data)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)

    def test_owner_reviews_renter_negative_impact(self):
        """Owner giving 1 star reduces renter's trust score by 20."""
        self.rental.status = RentalStatus.COMPLETED
        self.rental.save()

        renter_profile, _ = TrustProfile.objects.get_or_create(user=self.renter)
        initial_score = renter_profile.trust_score

        self.client.force_authenticate(user=self.owner)
        data = {
            'rental_id': self.rental.id,
            'target_type': ReviewTargetType.RENTER,
            'rating': 1,
            'comment': 'Returned asset late without notice.'
        }
        response = self.client.post('/api/reviews/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        renter_profile.refresh_from_db()
        self.assertEqual(renter_profile.trust_score, initial_score - 20)
        self.assertTrue(renter_profile.events.filter(event_type=TrustEventType.NEGATIVE_REVIEW).exists())

    def test_duplicate_review_prevention(self):
        """A user cannot submit duplicate reviews for the same target on a rental."""
        self.rental.status = RentalStatus.COMPLETED
        self.rental.save()

        self.client.force_authenticate(user=self.renter)
        data = {
            'rental_id': self.rental.id,
            'target_type': ReviewTargetType.OWNER,
            'rating': 5,
            'comment': 'Great owner'
        }
        r1 = self.client.post('/api/reviews/', data)
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)

        r2 = self.client.post('/api/reviews/', data)
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already submitted a review", str(r2.data))

    def test_unauthorized_user_cannot_review(self):
        """Users unrelated to the rental cannot submit reviews."""
        self.rental.status = RentalStatus.COMPLETED
        self.rental.save()

        self.client.force_authenticate(user=self.other_user)
        data = {
            'rental_id': self.rental.id,
            'target_type': ReviewTargetType.OWNER,
            'rating': 5,
            'comment': 'Fake review attempt'
        }
        response = self.client.post('/api/reviews/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
