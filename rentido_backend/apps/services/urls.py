from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceProviderViewSet, ServiceRequestViewSet

app_name = 'services'

router = DefaultRouter()
router.register(r'providers', ServiceProviderViewSet, basename='provider')
router.register(r'repair-requests', ServiceRequestViewSet, basename='repair-request')

urlpatterns = [
    path('', include(router.urls)),
]
