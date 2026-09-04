from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.categories.models import Category


class AssetCondition(models.TextChoices):
    NEW = 'NEW', _('Brand New')
    LIKE_NEW = 'LIKE_NEW', _('Like New')
    GOOD = 'GOOD', _('Good Condition')
    FAIR = 'FAIR', _('Fair / Functional')


class VerificationStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending Verification')
    UNDER_REVIEW = 'UNDER_REVIEW', _('Under Review')
    VERIFIED = 'VERIFIED', _('Verified')
    REJECTED = 'REJECTED', _('Rejected')


class AssetStatus(models.TextChoices):
    DRAFT = 'DRAFT', _('Draft')
    AVAILABLE = 'AVAILABLE', _('Available')
    RENTED = 'RENTED', _('Currently Rented')
    MAINTENANCE = 'MAINTENANCE', _('In Maintenance / Repair')
    RETIRED = 'RETIRED', _('Retired')


class Asset(models.Model):
    """
    Represents the tangible, physical asset independently of its marketplace listing.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assets'
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='assets'
    )
    name = models.CharField(max_length=200, help_text="e.g. Sony Alpha A7 III")
    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    condition = models.CharField(
        max_length=20, choices=AssetCondition.choices, default=AssetCondition.GOOD
    )
    replacement_value = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Estimated replacement value in local currency"
    )
    verification_status = models.CharField(
        max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.PENDING
    )
    status = models.CharField(
        max_length=20, choices=AssetStatus.choices, default=AssetStatus.DRAFT
    )
    ownership_document = models.FileField(
        upload_to='assets/documents/', null=True, blank=True, help_text="Invoice or ownership proof"
    )
    notes = models.TextField(blank=True, help_text="Internal notes or verification remarks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Physical Asset')
        verbose_name_plural = _('Physical Assets')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand} {self.model_name} (SN: {self.serial_number})"


class AssetMedia(models.Model):
    """
    Physical verification and inspection photos of the asset.
    """
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='media')
    image = models.ImageField(upload_to='assets/photos/')
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Asset Media')
        verbose_name_plural = _('Asset Media')

    def __str__(self):
        return f"Media for {self.asset.name}"
