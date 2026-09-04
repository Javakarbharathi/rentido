import random
from rest_framework import serializers
from .models import (
    Rental,
    RentalPricingSnapshot,
    RentalExtension,
    RentalAgreement,
    AgreementAddendum,
    RentalStatus,
    FulfillmentType,
    ExtensionStatus,
)
from .services.availability import AvailabilityService
from .services.pricing import PricingEngine
from apps.listings.models import Listing
from apps.listings.serializers import ListingSerializer


class RentalPricingSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalPricingSnapshot
        fields = [
            'id', 'base_rental_amount', 'platform_commission_rate',
            'platform_commission_amount', 'platform_fee', 'delivery_fee',
            'security_deposit_amount', 'total_amount_paid', 'owner_payout_amount',
            'raw_calculation', 'created_at'
        ]
        read_only_fields = fields


class QuoteRequestSerializer(serializers.Serializer):
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source='listing'
    )
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    fulfillment_type = serializers.ChoiceField(
        choices=FulfillmentType.choices, default=FulfillmentType.SELF_PICKUP
    )

    def validate(self, attrs):
        is_avail, reason = AvailabilityService.check_availability(
            listing=attrs['listing'],
            start_datetime=attrs['start_datetime'],
            end_datetime=attrs['end_datetime']
        )
        if not is_avail:
            raise serializers.ValidationError({"availability": reason})
        return attrs


class RentalBookingSerializer(serializers.Serializer):
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source='listing'
    )
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    fulfillment_type = serializers.ChoiceField(
        choices=FulfillmentType.choices, default=FulfillmentType.SELF_PICKUP
    )

    def validate(self, attrs):
        user = self.context['request'].user
        listing = attrs['listing']

        if listing.asset.owner == user:
            raise serializers.ValidationError("Owners cannot rent their own assets.")

        is_avail, reason = AvailabilityService.check_availability(
            listing=listing,
            start_datetime=attrs['start_datetime'],
            end_datetime=attrs['end_datetime']
        )
        if not is_avail:
            raise serializers.ValidationError({"availability": reason})

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        listing = validated_data['listing']
        start_datetime = validated_data['start_datetime']
        end_datetime = validated_data['end_datetime']
        fulfillment_type = validated_data['fulfillment_type']

        # 1. Compute frozen pricing
        pricing = PricingEngine.calculate_pricing(
            listing=listing,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            fulfillment_type=fulfillment_type
        )

        # 2. Generate secure 6-digit OTPs
        handover_otp = f"{random.randint(100000, 999999)}"
        return_otp = f"{random.randint(100000, 999999)}"

        # 3. Create Rental in PAYMENT_PENDING state
        rental = Rental.objects.create(
            renter=user,
            owner=listing.asset.owner,
            listing=listing,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            fulfillment_type=fulfillment_type,
            status=RentalStatus.PAYMENT_PENDING,
            handover_otp=handover_otp,
            return_otp=return_otp
        )

        # 4. Save immutable pricing snapshot
        RentalPricingSnapshot.objects.create(
            rental=rental,
            base_rental_amount=pricing['base_rental_amount'],
            platform_commission_rate=pricing['platform_commission_rate'],
            platform_commission_amount=pricing['platform_commission_amount'],
            platform_fee=pricing['platform_fee'],
            delivery_fee=pricing['delivery_fee'],
            security_deposit_amount=pricing['security_deposit_amount'],
            total_amount_paid=pricing['total_amount_paid'],
            owner_payout_amount=pricing['owner_payout_amount'],
            raw_calculation=pricing['raw_calculation']
        )

        return rental


class AgreementAddendumSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgreementAddendum
        fields = [
            'id', 'addendum_number', 'extended_until', 'additional_amount_paid',
            'terms_addendum', 'created_at'
        ]
        read_only_fields = fields


class RentalAgreementSerializer(serializers.ModelSerializer):
    addendums = AgreementAddendumSerializer(many=True, read_only=True)

    class Meta:
        model = RentalAgreement
        fields = [
            'id', 'agreement_number', 'terms_and_conditions',
            'signed_at', 'is_active', 'addendums'
        ]
        read_only_fields = fields


class RentalExtensionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    addendum = AgreementAddendumSerializer(read_only=True)

    class Meta:
        model = RentalExtension
        fields = [
            'id', 'rental', 'previous_end_datetime', 'new_end_datetime',
            'additional_rental_amount', 'additional_commission_amount',
            'additional_platform_fee', 'total_extension_amount',
            'status', 'status_display', 'is_approved_by_owner', 'is_paid',
            'reason', 'rejection_reason', 'addendum', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class RentalSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    pricing_snapshot = RentalPricingSnapshotSerializer(read_only=True)
    agreement = RentalAgreementSerializer(read_only=True)
    extensions = RentalExtensionSerializer(many=True, read_only=True)
    renter_email = serializers.ReadOnlyField(source='renter.email')
    owner_email = serializers.ReadOnlyField(source='owner.email')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    fulfillment_type_display = serializers.CharField(source='get_fulfillment_type_display', read_only=True)

    class Meta:
        model = Rental
        fields = [
            'id', 'renter', 'renter_email', 'owner', 'owner_email',
            'listing', 'start_datetime', 'end_datetime', 'fulfillment_type',
            'fulfillment_type_display', 'status', 'status_display',
            'handover_otp', 'return_otp', 'pricing_snapshot', 'agreement',
            'extensions', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class VerifyOTPActionSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, min_length=6)


class RequestExtensionSerializer(serializers.Serializer):
    new_end_datetime = serializers.DateTimeField()
    reason = serializers.CharField(required=False, allow_blank=True)


class OwnerDecideExtensionSerializer(serializers.Serializer):
    approve = serializers.BooleanField(required=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)


class PayExtensionSerializer(serializers.Serializer):
    payment_method = serializers.CharField(default='UPI')
