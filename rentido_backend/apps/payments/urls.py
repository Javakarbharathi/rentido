from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, SecurityDepositViewSet, LedgerViewSet

app_name = 'payments'

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'deposits', SecurityDepositViewSet, basename='deposit')
router.register(r'ledger', LedgerViewSet, basename='ledger')

urlpatterns = [
    # Clean direct gateway routes
    path('razorpay/create-order/', PaymentViewSet.as_view({'post': 'razorpay_create_order'}), name='razorpay-create-order'),
    path('razorpay/verify/', PaymentViewSet.as_view({'post': 'razorpay_verify_payment'}), name='razorpay-verify'),
    path('razorpay/webhook/', PaymentViewSet.as_view({'post': 'razorpay_webhook'}), name='razorpay-webhook'),
    path('stripe/create-intent/', PaymentViewSet.as_view({'post': 'stripe_create_intent'}), name='stripe-create-intent'),
    path('stripe/webhook/', PaymentViewSet.as_view({'post': 'stripe_webhook'}), name='stripe-webhook'),
    
    # ViewSet router endpoints
    path('', include(router.urls)),
]

