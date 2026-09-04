from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrustProfileViewSet

app_name = 'trust'

router = DefaultRouter()
router.register(r'trust', TrustProfileViewSet, basename='trust-profile')

urlpatterns = [
    path('', include(router.urls)),
]
