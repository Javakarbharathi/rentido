from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.listings.models import Listing


class RentalStatus(models.TextChoices):
    PAYMENT_PENDING = 'PAYMENT_PENDING', _('Payment Pending')
    CONFIRMED = 'CONFIRMED', _('Confirmed')
    READY_FOR_HANDOVER = 'READY_FOR_HANDOVER', _('Ready for Handover')
    HANDOVER_IN_PROGRESS = 'HANDOVER_IN_PROGRESS', _('Handover in Progress')
    ACTIVE = 'ACTIVE', _('Active Rental')
    EXTENSION_PENDING = 'EXTENSION_PENDING', _('Extension Pending')
    RETURN_REQUESTED = 'RETURN_REQUESTED', _('Return Requested')
    RETURN_IN_PROGRESS = 'RETURN_IN_PROGRESS', _('Return in Progress')
    INSPECTION_PENDING = 'INSPECTION_PENDING', _('Inspection Pending')
    COMPLETED = 'COMPLETED', _('Completed')
    CANCELLED = 'CANCELLED', _('Cancelled')
    DISPUTED = 'DISPUTED', _('Disputed')


class FulfillmentType(models.TextChoices):
    SELF_PICKUP = 'SELF_PICKUP', _('Self Pickup')
    DRIVER_DELIVERY = 'DRIVER_DELIVERY', _('Driver Delivery')
    HUB_PICKUP = 'HUB_PICKUP', _('Hub Pickup')


class Rental(models.Model):
    """
    Core Rental entity managing the long-running lifecycle between Renter and Owner.
    """
    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='rentals_as_renter'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='rentals_as_owner'
    )
    listing = models.ForeignKey(
        Listing, on_delete=models.PROTECT, related_name='rentals'
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    fulfillment_type = models.CharField(
        max_length=30, choices=FulfillmentType.choices, default=FulfillmentType.SELF_PICKUP
    )
    status = models.CharField(
        max_length=30, choices=RentalStatus.choices, default=RentalStatus.PAYMENT_PENDING
    )
    
    # Handover & Return Verification OTPs
    handover_otp = models.CharField(max_length=6, blank=True)
    return_otp = models.CharField(max_length=6, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Rental')
        verbose_name_plural = _('Rentals')
        ordering = ['-created_at']

    def __str__(self):
        return f"Rental #{self.id} — {self.listing.title} ({self.get_status_display()})"


class RentalPricingSnapshot(models.Model):
    """
    Immutable pricing snapshot captured at booking confirmation.
    Future commission or fee rule changes will not alter historical transactions.
    """
    rental = models.OneToOneField(
        Rental, on_delete=models.CASCADE, related_name='pricing_snapshot'
    )
    base_rental_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    platform_commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    security_deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    owner_payout_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raw_calculation = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Snapshot for Rental #{self.rental_id}: Paid ₹{self.total_amount_paid}"


class ExtensionStatus(models.TextChoices):
    PENDING_APPROVAL = 'PENDING_APPROVAL', _('Pending Owner Approval')
    APPROVED = 'APPROVED', _('Approved by Owner (Awaiting Payment)')
    PAID = 'PAID', _('Paid & Confirmed')
    REJECTED = 'REJECTED', _('Rejected by Owner')
    CANCELLED = 'CANCELLED', _('Cancelled')


class RentalExtension(models.Model):
    """
    Tracks requested rental extensions without directly overwriting original timestamps.
    """
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='extensions')
    previous_end_datetime = models.DateTimeField()
    new_end_datetime = models.DateTimeField()
    additional_rental_amount = models.DecimalField(max_digits=10, decimal_places=2)
    additional_commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    additional_platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_extension_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, choices=ExtensionStatus.choices, default=ExtensionStatus.PENDING_APPROVAL)
    reason = models.CharField(max_length=255, blank=True)
    rejection_reason = models.CharField(max_length=255, blank=True)
    is_approved_by_owner = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Rental Extension')
        verbose_name_plural = _('Rental Extensions')
        ordering = ['-created_at']

    def __str__(self):
        return f"Extension for Rental #{self.rental_id} to {self.new_end_datetime} ({self.get_status_display()})"


class RentalAgreement(models.Model):
    """
    Legally binding rental agreement generated upon booking confirmation.
    """
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE, related_name='agreement')
    agreement_number = models.CharField(max_length=100, unique=True)
    terms_and_conditions = models.TextField()
    signed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Rental Agreement')
        verbose_name_plural = _('Rental Agreements')

    def __str__(self):
        return f"Agreement {self.agreement_number} (Rental #{self.rental_id})"


class AgreementAddendum(models.Model):
    """
    Addendum to the original Rental Agreement generated upon a confirmed extension.
    """
    rental_agreement = models.ForeignKey(RentalAgreement, on_delete=models.CASCADE, related_name='addendums')
    rental_extension = models.OneToOneField(RentalExtension, on_delete=models.CASCADE, related_name='addendum')
    addendum_number = models.CharField(max_length=100, unique=True)
    extended_until = models.DateTimeField()
    additional_amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    terms_addendum = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Agreement Addendum')
        verbose_name_plural = _('Agreement Addendums')

    def __str__(self):
        return f"Addendum {self.addendum_number} for Agreement {self.rental_agreement.agreement_number}"
