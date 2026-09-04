from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CommissionRuleViewSet

app_name = 'categories'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'commission-rules', CommissionRuleViewSet, basename='commission-rule')

urlpatterns = [
    path('', include(router.urls)),
]
