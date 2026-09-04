from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class TrustTier(models.TextChoices):
    BRONZE = 'BRONZE', _('Bronze (New / Unverified)')
    SILVER = 'SILVER', _('Silver (Standard Trusted)')
    GOLD = 'GOLD', _('Gold (High Trust / Experienced)')
    PLATINUM = 'PLATINUM', _('Platinum (Elite Marketplace Star)')


class TrustEventType(models.TextChoices):
    KYC_VERIFIED = 'KYC_VERIFIED', _('Identity / KYC Verified (+50)')
    RENTAL_COMPLETED = 'RENTAL_COMPLETED', _('Successful Rental Completed (+15)')
    ON_TIME_RETURN = 'ON_TIME_RETURN', _('Asset Returned On-Time (+10)')
    POSITIVE_REVIEW = 'POSITIVE_REVIEW', _('Received 4 or 5 Star Review (+15)')
    NEGATIVE_REVIEW = 'NEGATIVE_REVIEW', _('Received 1 or 2 Star Review (-20)')
    LATE_RETURN = 'LATE_RETURN', _('Late Return Incident (-15)')
    DAMAGE_INCIDENT = 'DAMAGE_INCIDENT', _('Asset Damaged Incident (-30)')
    DISPUTE_RAISED = 'DISPUTE_RAISED', _('Dispute Filed Against User (-25)')


class TrustProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trust_profile')
    trust_score = models.IntegerField(default=150, help_text="Dynamic score between 0 and 1000")
    tier = models.CharField(max_length=20, choices=TrustTier.choices, default=TrustTier.SILVER)
    completed_rentals_count = models.IntegerField(default=0)
    dispute_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Trust Profile')
        verbose_name_plural = _('Trust Profiles')

    def __str__(self):
        return f"{self.user.email} — Score: {self.trust_score} ({self.get_tier_display()})"


class TrustEvent(models.Model):
    profile = models.ForeignKey(TrustProfile, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=40, choices=TrustEventType.choices)
    score_delta = models.IntegerField(help_text="Positive or negative score adjustment")
    description = models.CharField(max_length=255)
    reference_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Trust Event')
        verbose_name_plural = _('Trust Events')
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d')}] {self.get_event_type_display()} ({self.score_delta:+d})"
