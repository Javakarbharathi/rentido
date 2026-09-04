from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, AdminOperationsViewSet

app_name = 'audit'

router = DefaultRouter()
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'admin-ops', AdminOperationsViewSet, basename='admin-op')

urlpatterns = [
    path('', include(router.urls)),
]
