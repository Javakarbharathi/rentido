from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InspectionViewSet, DamageReportViewSet

app_name = 'inspections'

router = DefaultRouter()
router.register(r'inspections', InspectionViewSet, basename='inspection')
router.register(r'damage-reports', DamageReportViewSet, basename='damage-report')

urlpatterns = [
    path('', include(router.urls)),
]
