from apps.trust.models import TrustProfile, TrustEvent, TrustEventType, TrustTier


class TrustScoreEngine:
    """
    Computes real-time Rentido Trust Scores based on positive and negative marketplace events.
    """
    DEFAULT_DELTAS = {
        TrustEventType.KYC_VERIFIED: 50,
        TrustEventType.RENTAL_COMPLETED: 15,
        TrustEventType.ON_TIME_RETURN: 10,
        TrustEventType.POSITIVE_REVIEW: 15,
        TrustEventType.NEGATIVE_REVIEW: -20,
        TrustEventType.LATE_RETURN: -15,
        TrustEventType.DAMAGE_INCIDENT: -30,
        TrustEventType.DISPUTE_RAISED: -25,
    }

    @classmethod
    def record_event(cls, user, event_type, reference_id="", custom_delta=None, description=""):
        profile, _ = TrustProfile.objects.get_or_create(user=user)

        delta = custom_delta if custom_delta is not None else cls.DEFAULT_DELTAS.get(event_type, 0)
        new_score = max(min(profile.trust_score + delta, 1000), 0)

        # Recalculate Tier
        if new_score >= 650:
            tier = TrustTier.PLATINUM
        elif new_score >= 400:
            tier = TrustTier.GOLD
        elif new_score >= 150:
            tier = TrustTier.SILVER
        else:
            tier = TrustTier.BRONZE

        profile.trust_score = new_score
        profile.tier = tier

        if event_type == TrustEventType.RENTAL_COMPLETED:
            profile.completed_rentals_count += 1
        elif event_type == TrustEventType.DISPUTE_RAISED:
            profile.dispute_count += 1

        profile.save()

        # Log immutable event record
        event = TrustEvent.objects.create(
            profile=profile,
            event_type=event_type,
            score_delta=delta,
            description=description or f"Event: {event_type}",
            reference_id=reference_id
        )

        return profile, event
