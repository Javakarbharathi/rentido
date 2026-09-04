from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    UserProfileView,
    UpdateRenterProfileView,
    UpdateOwnerProfileView,
    AddRoleView,
)

app_name = 'users'

urlpatterns = [
    # Auth endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile endpoints
    path('me/', UserProfileView.as_view(), name='me'),
    path('me/renter/', UpdateRenterProfileView.as_view(), name='renter_profile'),
    path('me/owner/', UpdateOwnerProfileView.as_view(), name='owner_profile'),
    path('me/roles/add/', AddRoleView.as_view(), name='add_role'),
]
