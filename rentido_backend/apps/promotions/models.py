from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class DiscountType(models.TextChoices):
    PERCENTAGE = 'PERCENTAGE', _('Percentage Discount (%)')
    FLAT = 'FLAT', _('Flat Monetary Discount (₹)')


class Coupon(models.Model):
    """
    Platform-wide promotional discount coupons.
    """
    code = models.CharField(max_length=30, unique=True, db_index=True)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    discount_type = models.CharField(
        max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Optional maximum discount cap for percentage discounts"
    )
    minimum_rental_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text="Minimum base rent required to activate discount"
    )
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    usage_limit_total = models.PositiveIntegerField(default=1000)
    usage_limit_per_user = models.PositiveIntegerField(default=1)
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} — {self.discount_value}{'%' if self.discount_type == DiscountType.PERCENTAGE else ' OFF'}"

    def is_valid_now(self):
        if not self.is_active:
            return False, "This coupon is no longer active."
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False, "This coupon is not yet valid."
        if self.valid_until and now > self.valid_until:
            return False, "This coupon has expired."
        if self.times_used >= self.usage_limit_total:
            return False, "This coupon has reached its total usage limit."
        return True, "Valid"

    def calculate_discount(self, base_amount):
        if base_amount < self.minimum_rental_amount:
            return Decimal('0.00'), f"Minimum rental amount of {self.minimum_rental_amount} required."

        if self.discount_type == DiscountType.PERCENTAGE:
            discount = (base_amount * self.discount_value / Decimal('100.00')).quantize(Decimal('0.01'))
            if self.max_discount_amount and discount > self.max_discount_amount:
                discount = self.max_discount_amount
        else:
            discount = min(self.discount_value, base_amount).quantize(Decimal('0.01'))

        return discount, "Discount applied."


class CouponRedemption(models.Model):
    """
    Audit log of coupon redemptions tied to user and optional rental.
    """
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name='redemptions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupon_redemptions')
    rental = models.ForeignKey(
        'rentals.Rental', on_delete=models.SET_NULL, null=True, blank=True, related_name='coupon_redemptions'
    )
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Coupon Redemption')
        verbose_name_plural = _('Coupon Redemptions')
        ordering = ['-redeemed_at']

    def __str__(self):
        return f"{self.user.email} used {self.coupon.code} (-₹{self.discount_applied})"


class SurgePricingRule(models.Model):
    """
    Dynamic surge multiplier applied during festivals, peak weekends, or citywide demand spikes.
    """
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100, blank=True, help_text="Blank applies to all cities")
    category = models.ForeignKey(
        'categories.Category', on_delete=models.CASCADE, null=True, blank=True,
        help_text="Blank applies to all categories"
    )
    multiplier = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal('1.00'),
        help_text="e.g. 1.20 represents a 20% surge"
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Surge Pricing Rule')
        verbose_name_plural = _('Surge Pricing Rules')
        ordering = ['-start_datetime']

    def __str__(self):
        scope = f"{self.city or 'All Cities'} / {self.category.name if self.category else 'All Categories'}"
        return f"{self.name} ({scope}): {self.multiplier}x"


class ReferralCode(models.Model):
    """
    Unique referral code per registered user.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_code'
    )
    code = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} -> {self.code}"


class ReferralReward(models.Model):
    """
    Tracks referral relationships and awards trust points / credits on first rental.
    """
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referrals_sent'
    )
    referee = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_received'
    )
    reward_points = models.IntegerField(default=25)
    is_awarded = models.BooleanField(default=False)
    awarded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Referral Reward')
        verbose_name_plural = _('Referral Rewards')

    def __str__(self):
        status_txt = "Awarded" if self.is_awarded else "Pending"
        return f"{self.referrer.email} referred {self.referee.email} ({status_txt})"
