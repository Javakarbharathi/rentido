from rest_framework import serializers
from .models import (
    ServiceProvider,
    ServiceRequest,
    ServiceCategory,
    ServiceRequestStatus,
    ServiceCommissionRule,
)
from apps.assets.models import Asset
from apps.assets.serializers import AssetSerializer
from apps.users.models import RoleChoices, UserRole


class ServiceProviderSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = ServiceProvider
        fields = [
            'id', 'user', 'user_email', 'category', 'category_display',
            'business_name', 'phone_number', 'address', 'city', 'pincode',
            'experience_years', 'rating', 'is_verified', 'is_available',
            'base_diagnostic_fee', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'rating', 'is_verified', 'created_at']


class ServiceProviderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = [
            'id', 'category', 'business_name', 'phone_number', 'address',
            'city', 'pincode', 'experience_years', 'base_diagnostic_fee'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user

        # Ensure user has SERVICE_PROVIDER role
        if not user.has_role(RoleChoices.SERVICE_PROVIDER):
            UserRole.objects.get_or_create(user=user, role=RoleChoices.SERVICE_PROVIDER, defaults={'is_active': True})

        return super().create(validated_data)


class ServiceRequestSerializer(serializers.ModelSerializer):
    asset_details = AssetSerializer(source='asset', read_only=True)
    provider_details = ServiceProviderSerializer(source='assigned_provider', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'asset', 'asset_details', 'damage_report', 'requested_by',
            'assigned_provider', 'provider_details', 'category', 'category_display',
            'issue_title', 'description', 'status', 'status_display',
            'final_quote_amount', 'platform_commission', 'provider_payout',
            'quote_notes', 'is_quote_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'asset', 'damage_report', 'assigned_provider',
            'category', 'issue_title', 'description'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['requested_by'] = self.context['request'].user
        return super().create(validated_data)


class SubmitQuoteSerializer(serializers.Serializer):
    final_quote_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    quote_notes = serializers.CharField(required=False, allow_blank=True)


class ApproveQuoteSerializer(serializers.Serializer):
    payment_method = serializers.CharField(default='UPI')
