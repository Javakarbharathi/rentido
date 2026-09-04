from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Coupon, SurgePricingRule, ReferralCode, ReferralReward
from .serializers import (
    CouponSerializer,
    CouponValidateSerializer,
    SurgePricingRuleSerializer,
    ReferralClaimSerializer,
)
from .services.promotions import PromotionService
from apps.rentals.services.pricing import PricingEngine


@extend_schema_view(
    list=extend_schema(summary="Browse active promotional coupons"),
    retrieve=extend_schema(summary="Retrieve coupon details")
)
class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Validate coupon and preview rental discount before booking",
        request=CouponValidateSerializer
    )
    @action(detail=False, methods=['post'], url_path='validate', permission_classes=[permissions.AllowAny])
    def validate_coupon(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        listing = serializer.validated_data['listing']
        start_datetime = serializer.validated_data['start_datetime']
        end_datetime = serializer.validated_data['end_datetime']

        # Calculate pricing with coupon preview
        pricing = PricingEngine.calculate_pricing(
            listing=listing,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            user=request.user if request.user.is_authenticated else None,
            coupon_code=code
        )

        if pricing['discount_amount'] > 0:
            return Response({
                "valid": True,
                "coupon_code": pricing['coupon_code'],
                "discount_amount": pricing['discount_amount'],
                "new_total": pricing['total_amount_paid'],
                "message": pricing['coupon_message']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "valid": False,
                "discount_amount": "0.00",
                "message": pricing['coupon_message'] or "Coupon could not be applied."
            }, status=status.HTTP_400_BAD_REQUEST)


class SurgePricingRuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SurgePricingRule.objects.filter(is_active=True)
    serializer_class = SurgePricingRuleSerializer
    permission_classes = [permissions.AllowAny]


class ReferralViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Get authenticated user's referral code and tracking stats")
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        code = PromotionService.get_or_create_referral_code(request.user)
        referrals = ReferralReward.objects.filter(referrer=request.user)
        awarded_count = referrals.filter(is_awarded=True).count()
        pending_count = referrals.filter(is_awarded=False).count()

        return Response({
            "referral_code": code,
            "referral_link": f"https://rentido.com/signup?ref={code}",
            "total_referred": referrals.count(),
            "rewards_awarded": awarded_count,
            "rewards_pending": pending_count,
            "reward_points_per_referral": 25
        })

    @extend_schema(summary="Claim a friend's referral code upon joining", request=ReferralClaimSerializer)
    @action(detail=False, methods=['post'], url_path='claim')
    def claim(self, request):
        serializer = ReferralClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code_str = serializer.validated_data['referral_code']
        success, message = PromotionService.link_referral(
            referee=request.user,
            referral_code_str=code_str
        )

        if success:
            return Response({"status": "SUCCESS", "message": message}, status=status.HTTP_200_OK)
        return Response({"status": "ERROR", "message": message}, status=status.HTTP_400_BAD_REQUEST)
