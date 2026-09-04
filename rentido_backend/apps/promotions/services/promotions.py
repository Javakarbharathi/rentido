from decimal import Decimal
from django.utils import timezone
from apps.promotions.models import (
    Coupon,
    CouponRedemption,
    SurgePricingRule,
    ReferralCode,
    ReferralReward,
)
from apps.trust.services.scoring import TrustScoreEngine
from apps.trust.models import TrustEventType


class PromotionService:
    @classmethod
    def validate_coupon(cls, code, user, base_amount):
        """
        Validates coupon availability and calculates discounted amount.
        """
        code = (code or "").strip().upper()
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return {"valid": False, "discount": Decimal('0.00'), "message": "Invalid coupon code."}

        is_valid, msg = coupon.is_valid_now()
        if not is_valid:
            return {"valid": False, "discount": Decimal('0.00'), "message": msg}

        if user and user.is_authenticated:
            user_used = CouponRedemption.objects.filter(coupon=coupon, user=user).count()
            if user_used >= coupon.usage_limit_per_user:
                return {
                    "valid": False,
                    "discount": Decimal('0.00'),
                    "message": "You have already reached the usage limit for this coupon."
                }

        discount, calc_msg = coupon.calculate_discount(base_amount)
        if discount <= 0:
            return {"valid": False, "discount": Decimal('0.00'), "message": calc_msg}

        return {
            "valid": True,
            "coupon": coupon,
            "coupon_id": coupon.id,
            "code": coupon.code,
            "discount": discount,
            "message": f"Coupon applied! You saved ₹{discount}."
        }

    @classmethod
    def redeem_coupon(cls, coupon, user, rental, discount_amount):
        """
        Records official redemption of a coupon.
        """
        coupon.times_used += 1
        coupon.save(update_fields=['times_used'])

        redemption = CouponRedemption.objects.create(
            coupon=coupon,
            user=user,
            rental=rental,
            discount_applied=discount_amount
        )
        return redemption

    @classmethod
    def get_surge_multiplier(cls, city=None, category=None, target_datetime=None):
        """
        Determines current dynamic surge multiplier.
        """
        target_datetime = target_datetime or timezone.now()
        rules = SurgePricingRule.objects.filter(
            is_active=True,
            start_datetime__lte=target_datetime,
            end_datetime__gte=target_datetime
        )

        multipliers = [Decimal('1.00')]
        for rule in rules:
            city_match = not rule.city or (city and rule.city.lower() == city.lower())
            category_match = not rule.category or (category and rule.category_id == category.id)
            if city_match and category_match:
                multipliers.append(rule.multiplier)

        return max(multipliers)

    @classmethod
    def get_or_create_referral_code(cls, user):
        """
        Generates or retrieves a unique referral code for a user.
        """
        code_obj, created = ReferralCode.objects.get_or_create(user=user, defaults={
            'code': f"{user.username[:6].upper()}{user.id}".replace('@', '').replace('.', '')
        })
        return code_obj.code

    @classmethod
    def link_referral(cls, referee, referral_code_str):
        """
        Links a newly registered user to their referrer.
        """
        referral_code_str = (referral_code_str or "").strip().upper()
        try:
            ref_code = ReferralCode.objects.select_related('user').get(code=referral_code_str)
        except ReferralCode.DoesNotExist:
            return False, "Referral code does not exist."

        if ref_code.user == referee:
            return False, "You cannot use your own referral code."

        if ReferralReward.objects.filter(referee=referee).exists():
            return False, "You have already used a referral code."

        reward = ReferralReward.objects.create(
            referrer=ref_code.user,
            referee=referee,
            reward_points=25
        )
        return True, f"Referral linked! Welcome bonus will activate upon your first rental completion."

    @classmethod
    def process_referral_completion(cls, referee):
        """
        Called when a user completes their first rental: awards trust points to referrer.
        """
        try:
            reward = ReferralReward.objects.get(referee=referee, is_awarded=False)
            reward.is_awarded = True
            reward.awarded_at = timezone.now()
            reward.save(update_fields=['is_awarded', 'awarded_at'])

            # Reward referrer with trust points
            TrustScoreEngine.record_event(
                user=reward.referrer,
                event_type=TrustEventType.RENTAL_COMPLETED,
                reference_id=f"REF-AWARD-{referee.id}",
                custom_delta=reward.reward_points,
                description=f"Referral reward: {referee.email} completed their first rental!"
            )
            return True
        except ReferralReward.DoesNotExist:
            return False
