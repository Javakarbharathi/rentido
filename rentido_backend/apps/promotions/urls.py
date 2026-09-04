from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, SurgePricingRuleViewSet, ReferralViewSet

app_name = 'promotions'

router = DefaultRouter()
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'surge-rules', SurgePricingRuleViewSet, basename='surge-rule')
router.register(r'referrals', ReferralViewSet, basename='referral')

urlpatterns = [
    path('', include(router.urls)),
]
