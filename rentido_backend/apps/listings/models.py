from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.assets.models import Asset


class PricingModel(models.TextChoices):
    HOURLY = 'HOURLY', _('Per Hour')
    DAILY = 'DAILY', _('Per Day')
    WEEKLY = 'WEEKLY', _('Per Week')
    MONTHLY = 'MONTHLY', _('Per Month')


class ListingStatus(models.TextChoices):
    DRAFT = 'DRAFT', _('Draft')
    PUBLISHED = 'PUBLISHED', _('Published / Active')
    PAUSED = 'PAUSED', _('Paused by Owner')
    ARCHIVED = 'ARCHIVED', _('Archived')


class Listing(models.Model):
    """
    Commercial rental listing created for a physical Asset.
    """
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    pricing_model = models.CharField(
        max_length=20, choices=PricingModel.choices, default=PricingModel.DAILY
    )
    security_deposit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Refundable security deposit held during rental"
    )
    
    # Location & Fulfillment
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=150, blank=True)
    pincode = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    is_self_pickup_available = models.BooleanField(default=True)
    is_delivery_available = models.BooleanField(default=False)
    
    status = models.CharField(
        max_length=20, choices=ListingStatus.choices, default=ListingStatus.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Rental Listing')
        verbose_name_plural = _('Rental Listings')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.rental_price}/{self.get_pricing_model_display()}"
