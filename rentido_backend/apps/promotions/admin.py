from django.contrib import admin
from .models import Coupon, CouponRedemption, SurgePricingRule, ReferralCode, ReferralReward


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'discount_type', 'discount_value', 'usage_limit_total', 'times_used', 'is_active', 'valid_until')
    list_filter = ('discount_type', 'is_active', 'created_at')
    search_fields = ('code', 'title')


@admin.register(CouponRedemption)
class CouponRedemptionAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'rental', 'discount_applied', 'redeemed_at')
    list_filter = ('redeemed_at',)
    search_fields = ('coupon__code', 'user__email')


@admin.register(SurgePricingRule)
class SurgePricingRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'category', 'multiplier', 'start_datetime', 'end_datetime', 'is_active')
    list_filter = ('is_active', 'city')
    search_fields = ('name', 'city')


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__email', 'code')


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referee', 'reward_points', 'is_awarded', 'awarded_at')
    list_filter = ('is_awarded', 'created_at')
    search_fields = ('referrer__email', 'referee__email')
