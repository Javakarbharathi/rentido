"""
Rentido API URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth & Identity Endpoints
    path('api/auth/', include('apps.users.urls', namespace='users')),
    
    # Core Marketplace Endpoints
    path('api/', include('apps.categories.urls', namespace='categories')),
    path('api/', include('apps.assets.urls', namespace='assets')),
    path('api/', include('apps.listings.urls', namespace='listings')),
    path('api/', include('apps.rentals.urls', namespace='rentals')),
    path('api/', include('apps.payments.urls', namespace='payments')),
    path('api/', include('apps.inspections.urls', namespace='inspections')),
    path('api/', include('apps.logistics.urls', namespace='logistics')),
    path('api/', include('apps.services.urls', namespace='services')),
    
    # API Documentation (Swagger & ReDoc)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
