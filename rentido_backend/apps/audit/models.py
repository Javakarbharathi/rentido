from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditAction(models.TextChoices):
    ESCROW_RELEASED = 'ESCROW_RELEASED', _('Security Deposit Escrow Released')
    ESCROW_DEDUCTED = 'ESCROW_DEDUCTED', _('Damage Deduction from Escrow')
    DISPUTE_ARBITRATED = 'DISPUTE_ARBITRATED', _('Admin Arbitrated Dispute')
    ASSET_VERIFIED = 'ASSET_VERIFIED', _('Physical Asset Verified by Admin')
    ASSET_REJECTED = 'ASSET_REJECTED', _('Physical Asset Rejected by Admin')
    REFUND_ISSUED = 'REFUND_ISSUED', _('Manual Refund Issued')
    USER_ROLE_GRANTED = 'USER_ROLE_GRANTED', _('Administrative Role Granted')
    SYSTEM_CONFIG_UPDATED = 'SYSTEM_CONFIG_UPDATED', _('System Configuration Modified')


class AuditLogEntry(models.Model):
    """
    Immutable audit trail for high-impact platform operations.
    """
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs_authored'
    )
    action = models.CharField(max_length=50, choices=AuditAction.choices, db_index=True)
    target_model = models.CharField(max_length=50, db_index=True)
    target_id = models.CharField(max_length=50, db_index=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('Audit Log Entry')
        verbose_name_plural = _('Audit Log Entries')
        ordering = ['-timestamp']

    def __str__(self):
        actor_email = self.actor.email if self.actor else 'SYSTEM'
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {actor_email} -> {self.action} on {self.target_model} #{self.target_id}"
