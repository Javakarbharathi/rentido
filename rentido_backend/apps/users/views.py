from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import User, RenterProfile, OwnerProfile
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    RenterProfileSerializer,
    OwnerProfileSerializer,
    AddRoleSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    Register a new user with an initial role (Renter, Owner, Driver, or Service Provider).
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="User Registration",
        description="Creates a new user account with an initial role and auto-provisions their role profile.",
        responses={201: UserSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = UserSerializer(user).data
        return Response(user_data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint returning JWT access, refresh tokens, and user details with roles.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary="User Login (JWT)",
        description="Authenticate with email and password to receive JWT access and refresh tokens."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user's profile and active roles.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get / Update Current User Profile",
        description="Fetch detailed profile data including associated Renter and Owner profiles."
    )
    def get_object(self):
        return self.request.user


class UpdateRenterProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update specific Renter profile fields (address, emergency contact).
    """
    serializer_class = RenterProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Get / Update Renter Profile")
    def get_object(self):
        profile, _ = RenterProfile.objects.get_or_create(user=self.request.user)
        return profile


class UpdateOwnerProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update specific Owner profile fields (business name, tax ID).
    """
    serializer_class = OwnerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Get / Update Owner Profile")
    def get_object(self):
        profile, _ = OwnerProfile.objects.get_or_create(user=self.request.user)
        return profile


class AddRoleView(APIView):
    """
    Add a new role (e.g. an existing Renter activating an Owner profile).
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Add New Role to User",
        request=AddRoleSerializer,
        responses={200: OpenApiResponse(description="Role activated successfully")}
    )
    def post(self, request):
        serializer = AddRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            {"detail": f"Role '{serializer.validated_data['role']}' added successfully.",
             "user": UserSerializer(request.user).data},
            status=status.HTTP_200_OK
        )
