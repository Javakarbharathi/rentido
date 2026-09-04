from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RentalViewSet, RentalExtensionViewSet

app_name = 'rentals'

router = DefaultRouter()
router.register(r'rentals', RentalViewSet, basename='rental')
router.register(r'extensions', RentalExtensionViewSet, basename='extension')

urlpatterns = [
    path('', include(router.urls)),
]
