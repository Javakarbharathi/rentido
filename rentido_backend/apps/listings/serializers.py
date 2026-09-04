from rest_framework import serializers
from .models import Listing, ListingStatus, PricingModel
from apps.assets.models import Asset, VerificationStatus
from apps.assets.serializers import AssetSerializer


class ListingSerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)
    owner_email = serializers.ReadOnlyField(source='asset.owner.email')
    pricing_model_display = serializers.CharField(source='get_pricing_model_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'asset', 'owner_email', 'title', 'description',
            'rental_price', 'pricing_model', 'pricing_model_display',
            'security_deposit', 'city', 'area', 'pincode',
            'latitude', 'longitude', 'is_self_pickup_available',
            'is_delivery_available', 'status', 'status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ListingCreateSerializer(serializers.ModelSerializer):
    asset_id = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.all(), source='asset', write_only=True
    )

    class Meta:
        model = Listing
        fields = [
            'id', 'asset_id', 'title', 'description', 'rental_price',
            'pricing_model', 'security_deposit', 'city', 'area', 'pincode',
            'latitude', 'longitude', 'is_self_pickup_available',
            'is_delivery_available', 'status'
        ]
        read_only_fields = ['id']

    def validate_asset_id(self, value):
        user = self.context['request'].user
        if value.owner != user and not user.is_staff:
            raise serializers.ValidationError("You can only create listings for physical assets you own.")
        return value

    def create(self, validated_data):
        if 'status' not in validated_data or not validated_data['status']:
            validated_data['status'] = ListingStatus.PUBLISHED
        return super().create(validated_data)
