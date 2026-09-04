from rest_framework import serializers
from .models import Asset, AssetMedia, VerificationStatus, AssetCondition, AssetStatus
from apps.categories.serializers import CategorySerializer
from apps.users.models import RoleChoices, UserRole, OwnerProfile


class AssetMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetMedia
        fields = ['id', 'image', 'caption', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


class AssetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    media = AssetMediaSerializer(many=True, read_only=True)
    owner_email = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Asset
        fields = [
            'id', 'owner', 'owner_email', 'category', 'name', 'brand',
            'model_name', 'serial_number', 'condition', 'replacement_value',
            'verification_status', 'status', 'ownership_document',
            'notes', 'media', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner', 'owner_email', 'verification_status',
            'created_at', 'updated_at'
        ]


class AssetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            'id', 'category', 'name', 'brand', 'model_name',
            'serial_number', 'condition', 'replacement_value',
            'ownership_document', 'notes'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['owner'] = user
        validated_data['verification_status'] = VerificationStatus.PENDING
        validated_data['status'] = AssetStatus.DRAFT

        # Ensure user has the Owner role and profile
        if not user.has_role(RoleChoices.OWNER):
            UserRole.objects.get_or_create(user=user, role=RoleChoices.OWNER, defaults={'is_active': True})
        if not hasattr(user, 'owner_profile'):
            OwnerProfile.objects.get_or_create(user=user)

        return super().create(validated_data)


class AssetVerificationSerializer(serializers.Serializer):
    verification_status = serializers.ChoiceField(
        choices=[VerificationStatus.VERIFIED, VerificationStatus.REJECTED, VerificationStatus.UNDER_REVIEW]
    )
    notes = serializers.CharField(required=False, allow_blank=True)
