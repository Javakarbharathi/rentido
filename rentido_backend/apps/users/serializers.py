from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User, UserRole, RenterProfile, OwnerProfile, RoleChoices


class RenterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenterProfile
        fields = [
            'id', 'emergency_contact', 'address', 'city', 'state',
            'postal_code', 'kyc_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'kyc_verified', 'created_at', 'updated_at']


class OwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerProfile
        fields = [
            'id', 'business_name', 'tax_id', 'is_verified', 'rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'rating', 'created_at', 'updated_at']


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'role', 'is_active', 'assigned_at']


class UserSerializer(serializers.ModelSerializer):
    roles = UserRoleSerializer(many=True, read_only=True)
    renter_profile = RenterProfileSerializer(read_only=True)
    owner_profile = OwnerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone_number', 'is_email_verified', 'is_phone_verified',
            'profile_picture', 'roles', 'renter_profile', 'owner_profile',
            'is_staff', 'is_superuser',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_email_verified', 'is_phone_verified', 'is_staff', 'is_superuser', 'created_at', 'updated_at'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    initial_role = serializers.ChoiceField(
        choices=[
            (RoleChoices.RENTER, 'Renter'),
            (RoleChoices.OWNER, 'Owner'),
            (RoleChoices.DRIVER, 'Driver'),
            (RoleChoices.SERVICE_PROVIDER, 'Service Provider')
        ],
        default=RoleChoices.RENTER,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'phone_number', 'password', 'password_confirm', 'initial_role'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        initial_role = validated_data.pop('initial_role', RoleChoices.RENTER)
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)

        # Assign initial role
        UserRole.objects.create(user=user, role=initial_role, is_active=True)

        # Provision profile according to initial role
        if initial_role == RoleChoices.RENTER:
            RenterProfile.objects.create(user=user)
        elif initial_role == RoleChoices.OWNER:
            OwnerProfile.objects.create(user=user)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Enhanced JWT token serializer that embeds user info and roles into payload.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['username'] = user.username
        token['roles'] = list(user.roles.filter(is_active=True).values_list('role', flat=True))
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class AddRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=[
            (RoleChoices.RENTER, 'Renter'),
            (RoleChoices.OWNER, 'Owner'),
            (RoleChoices.DRIVER, 'Driver'),
            (RoleChoices.SERVICE_PROVIDER, 'Service Provider')
        ]
    )

    def save(self, user):
        role_name = self.validated_data['role']
        role_obj, created = UserRole.objects.get_or_create(
            user=user, role=role_name, defaults={'is_active': True}
        )
        if not created and not role_obj.is_active:
            role_obj.is_active = True
            role_obj.save()

        # Provision corresponding profile if missing
        if role_name == RoleChoices.RENTER and not hasattr(user, 'renter_profile'):
            RenterProfile.objects.create(user=user)
        elif role_name == RoleChoices.OWNER and not hasattr(user, 'owner_profile'):
            OwnerProfile.objects.create(user=user)

        return role_obj
