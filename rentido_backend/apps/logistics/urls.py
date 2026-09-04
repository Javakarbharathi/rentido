from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, DeliveryOrderViewSet

app_name = 'logistics'

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'deliveries', DeliveryOrderViewSet, basename='delivery')

urlpatterns = [
    path('', include(router.urls)),
]
