from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, SecurityDepositViewSet, LedgerViewSet

app_name = 'payments'

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'deposits', SecurityDepositViewSet, basename='deposit')
router.register(r'ledger', LedgerViewSet, basename='ledger')

urlpatterns = [
    path('', include(router.urls)),
]
