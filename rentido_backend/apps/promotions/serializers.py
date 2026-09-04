from rest_framework import serializers
from .models import Coupon, CouponRedemption, SurgePricingRule, ReferralCode, ReferralReward
from apps.listings.models import Listing


class CouponSerializer(serializers.ModelSerializer):
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'title', 'description', 'discount_type',
            'discount_type_display', 'discount_value', 'max_discount_amount',
            'minimum_rental_amount', 'valid_from', 'valid_until'
        ]
        read_only_fields = fields


class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    listing_id = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all(), source='listing')
    start_datetime = serializers.DateTimeField(required=True)
    end_datetime = serializers.DateTimeField(required=True)


class SurgePricingRuleSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = SurgePricingRule
        fields = [
            'id', 'name', 'city', 'category', 'category_name',
            'multiplier', 'start_datetime', 'end_datetime', 'is_active'
        ]
        read_only_fields = fields


class ReferralClaimSerializer(serializers.Serializer):
    referral_code = serializers.CharField(required=True, max_length=30)
