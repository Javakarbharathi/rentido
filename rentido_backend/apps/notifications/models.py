from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class NotificationChannel(models.TextChoices):
    IN_APP = 'IN_APP', _('In-App Notification')
    EMAIL = 'EMAIL', _('Email')
    SMS = 'SMS', _('SMS Text Message')
    PUSH = 'PUSH', _('Mobile Push Notification')


class NotificationType(models.TextChoices):
    RENTAL_BOOKED = 'RENTAL_BOOKED', _('Rental Booking Created')
    RENTAL_CONFIRMED = 'RENTAL_CONFIRMED', _('Rental Confirmed & Paid')
    OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', _('Out for Delivery')
    HANDOVER_OTP = 'HANDOVER_OTP', _('Handover Verification OTP')
    RETURN_REMINDER = 'RETURN_REMINDER', _('Return Window Approaching')
    OVERDUE_WARNING = 'OVERDUE_WARNING', _('Rental Overdue Warning')
    INSPECTION_FLAGGED = 'INSPECTION_FLAGGED', _('Inspection Discrepancy Found')
    DAMAGE_REPORTED = 'DAMAGE_REPORTED', _('Damage Report Filed')
    QUOTE_RECEIVED = 'QUOTE_RECEIVED', _('Repair Quote Submitted')
    QUOTE_ACCEPTED = 'QUOTE_ACCEPTED', _('Repair Quote Accepted')
    EXTENSION_REQUESTED = 'EXTENSION_REQUESTED', _('Rental Extension Requested')
    EXTENSION_RESOLVED = 'EXTENSION_RESOLVED', _('Rental Extension Decision')
    REVIEW_RECEIVED = 'REVIEW_RECEIVED', _('New Review Received')
    TRUST_SCORE_UPDATE = 'TRUST_SCORE_UPDATE', _('Trust Score & Tier Update')
    SYSTEM_ALERT = 'SYSTEM_ALERT', _('System Alert')


class Notification(models.Model):
    """
    Centralized notifications log for all marketplace participants.
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    channel = models.CharField(
        max_length=20, choices=NotificationChannel.choices, default=NotificationChannel.IN_APP
    )
    notification_type = models.CharField(
        max_length=40, choices=NotificationType.choices, default=NotificationType.SYSTEM_ALERT
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True, help_text="Contextual metadata payload")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.channel}] To: {self.recipient.email} - {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class NotificationPreference(models.Model):
    """
    User-configurable notification preference toggles.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences'
    )
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')

    def __str__(self):
        return f"Preferences for {self.user.email}"
