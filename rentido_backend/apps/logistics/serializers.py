import random
from rest_framework import serializers
from .models import (
    Vehicle,
    DeliveryOrder,
    TransportProof,
    LogisticsCommissionRule,
    VehicleType,
    DeliveryStatus,
)
from apps.users.models import RoleChoices, UserRole


class VehicleSerializer(serializers.ModelSerializer):
    driver_email = serializers.ReadOnlyField(source='driver.email')
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'driver', 'driver_email', 'vehicle_type', 'vehicle_type_display',
            'registration_number', 'make_model', 'max_payload_kg',
            'cargo_volume_cbm', 'is_verified', 'is_active', 'insurance_expiry',
            'created_at'
        ]
        read_only_fields = ['id', 'driver', 'is_verified', 'created_at']


class VehicleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_type', 'registration_number', 'make_model',
            'max_payload_kg', 'cargo_volume_cbm', 'insurance_expiry'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['driver'] = user

        # Ensure user has DRIVER role
        if not user.has_role(RoleChoices.DRIVER):
            UserRole.objects.get_or_create(user=user, role=RoleChoices.DRIVER, defaults={'is_active': True})

        return super().create(validated_data)


class TransportProofSerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)

    class Meta:
        model = TransportProof
        fields = ['id', 'delivery_order', 'stage', 'stage_display', 'image', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class DeliveryOrderSerializer(serializers.ModelSerializer):
    driver_email = serializers.ReadOnlyField(source='assigned_driver.email')
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    transport_proofs = TransportProofSerializer(many=True, read_only=True)

    class Meta:
        model = DeliveryOrder
        fields = [
            'id', 'rental', 'assigned_driver', 'driver_email',
            'vehicle', 'vehicle_details', 'pickup_address', 'pickup_city',
            'pickup_pincode', 'dropoff_address', 'dropoff_city', 'dropoff_pincode',
            'pickup_otp', 'delivery_otp', 'status', 'status_display',
            'transport_fee', 'driver_payout', 'platform_fee',
            'transport_proofs', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class AcceptDeliverySerializer(serializers.Serializer):
    vehicle_id = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), source='vehicle')


class VerifyDeliveryOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, min_length=6)
