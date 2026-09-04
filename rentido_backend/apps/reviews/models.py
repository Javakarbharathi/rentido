from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.rentals.models import Rental
from apps.assets.models import Asset


class ReviewTargetType(models.TextChoices):
    OWNER = 'OWNER', _('Renter reviewing Owner')
    RENTER = 'RENTER', _('Owner reviewing Renter')
    ASSET = 'ASSET', _('Renter reviewing Physical Asset')
    DRIVER = 'DRIVER', _('Renter reviewing Delivery Driver')


class Review(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_authored')
    reviewee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews_received'
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    target_type = models.CharField(max_length=20, choices=ReviewTargetType.choices)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="1 to 5 stars")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        unique_together = ('rental', 'reviewer', 'target_type')

    def __str__(self):
        return f"{self.rating}★ review by {self.reviewer.email} on Rental #{self.rental_id} ({self.get_target_type_display()})"
