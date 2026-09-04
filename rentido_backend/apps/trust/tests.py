from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, RoleChoices, UserRole
from apps.trust.models import TrustProfile, TrustEvent, TrustEventType, TrustTier
from apps.trust.services.scoring import TrustScoreEngine


class TrustEngineTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            email='alice@rentido.com',
            password='password123',
            first_name='Alice',
            last_name='Wonder'
        )
        UserRole.objects.create(user=self.user, role=RoleChoices.RENTER, is_active=True)

        self.bob = User.objects.create_user(
            username='bob',
            email='bob@rentido.com',
            password='password123',
            first_name='Bob',
            last_name='Builder'
        )
        UserRole.objects.create(user=self.bob, role=RoleChoices.OWNER, is_active=True)

    def test_default_trust_profile(self):
        """New users receive default 150 points (Silver Tier)."""
        profile, _ = TrustProfile.objects.get_or_create(user=self.user)
        self.assertEqual(profile.trust_score, 150)
        self.assertEqual(profile.tier, TrustTier.SILVER)
        self.assertEqual(profile.completed_rentals_count, 0)
        self.assertEqual(profile.dispute_count, 0)

    def test_score_increments_and_tier_transitions(self):
        """Points accumulate and tiers update correctly up to Platinum."""
        # 1. KYC Verified (+50) -> 200 (Silver)
        profile, event = TrustScoreEngine.record_event(
            user=self.user,
            event_type=TrustEventType.KYC_VERIFIED,
            reference_id="KYC-101"
        )
        self.assertEqual(profile.trust_score, 200)
        self.assertEqual(profile.tier, TrustTier.SILVER)
        self.assertEqual(event.score_delta, 50)

        # 2. Large positive delta to reach Gold (>= 400)
        TrustScoreEngine.record_event(
            user=self.user,
            event_type=TrustEventType.RENTAL_COMPLETED,
            custom_delta=200
        )
        profile.refresh_from_db()
        self.assertEqual(profile.trust_score, 400)
        self.assertEqual(profile.tier, TrustTier.GOLD)
        self.assertEqual(profile.completed_rentals_count, 1)

        # 3. Advance to Platinum (>= 650)
        TrustScoreEngine.record_event(
            user=self.user,
            event_type=TrustEventType.RENTAL_COMPLETED,
            custom_delta=260
        )
        profile.refresh_from_db()
        self.assertEqual(profile.trust_score, 660)
        self.assertEqual(profile.tier, TrustTier.PLATINUM)

        # 4. Cap at 1000
        TrustScoreEngine.record_event(
            user=self.user,
            event_type=TrustEventType.RENTAL_COMPLETED,
            custom_delta=500
        )
        profile.refresh_from_db()
        self.assertEqual(profile.trust_score, 1000)

    def test_negative_deltas_and_bronze_tier(self):
        """Severe incidents reduce score down to Bronze Tier."""
        profile, _ = TrustProfile.objects.get_or_create(user=self.bob)
        self.assertEqual(profile.trust_score, 150)

        # Dispute (-25) -> 125 (Bronze)
        TrustScoreEngine.record_event(
            user=self.bob,
            event_type=TrustEventType.DISPUTE_RAISED,
            reference_id="DISP-99"
        )
        profile.refresh_from_db()
        self.assertEqual(profile.trust_score, 125)
        self.assertEqual(profile.tier, TrustTier.BRONZE)
        self.assertEqual(profile.dispute_count, 1)

        # Clamping at 0
        TrustScoreEngine.record_event(
            user=self.bob,
            event_type=TrustEventType.DAMAGE_INCIDENT,
            custom_delta=-200
        )
        profile.refresh_from_db()
        self.assertEqual(profile.trust_score, 0)
        self.assertEqual(profile.tier, TrustTier.BRONZE)

    def test_trust_api_endpoints(self):
        """Test /api/trust/me/ and /api/trust/user/<id>/ endpoints."""
        TrustScoreEngine.record_event(
            user=self.user,
            event_type=TrustEventType.KYC_VERIFIED,
            reference_id="KYC-API-1"
        )

        # 1. /api/trust/me/
        self.client.force_authenticate(user=self.user)
        me_resp = self.client.get('/api/trust/me/')
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(me_resp.data['trust_score'], 200)
        self.assertEqual(me_resp.data['tier'], TrustTier.SILVER)
        self.assertEqual(len(me_resp.data['recent_events']), 1)
        self.assertEqual(me_resp.data['recent_events'][0]['reference_id'], "KYC-API-1")

        # 2. Public badge lookup for another user
        badge_resp = self.client.get(f'/api/trust/user/{self.user.id}/')
        self.assertEqual(badge_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(badge_resp.data['trust_score'], 200)
        self.assertEqual(badge_resp.data['tier'], TrustTier.SILVER)
