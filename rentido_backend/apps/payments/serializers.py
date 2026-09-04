from rest_framework import serializers
from .models import Payment, SecurityDeposit, LedgerEntry, PaymentMethod
from apps.rentals.models import Rental


class PaymentSerializer(serializers.ModelSerializer):
    payer_email = serializers.ReadOnlyField(source='payer.email')
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'rental', 'payer', 'payer_email', 'amount',
            'transaction_id', 'payment_method', 'status',
            'status_display', 'gateway_response', 'created_at'
        ]
        read_only_fields = ['id', 'payer', 'status', 'created_at']


class SecurityDepositSerializer(serializers.ModelSerializer):
    renter_email = serializers.ReadOnlyField(source='renter.email')
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SecurityDeposit
        fields = [
            'id', 'rental', 'renter', 'renter_email', 'total_amount',
            'refunded_amount', 'deducted_amount', 'status',
            'status_display', 'notes', 'held_at', 'settled_at'
        ]
        read_only_fields = fields


class LedgerEntrySerializer(serializers.ModelSerializer):
    entry_type_display = serializers.CharField(source='get_entry_type_display', read_only=True)

    class Meta:
        model = LedgerEntry
        fields = [
            'id', 'rental', 'entry_type', 'entry_type_display',
            'debit_account', 'credit_account', 'amount',
            'description', 'reference_id', 'timestamp'
        ]
        read_only_fields = fields


class InitiatePaymentSerializer(serializers.Serializer):
    rental_id = serializers.PrimaryKeyRelatedField(queryset=Rental.objects.all(), source='rental')
    payment_method = serializers.ChoiceField(
        choices=PaymentMethod.choices, default=PaymentMethod.UPI
    )


class SettleDepositSerializer(serializers.Serializer):
    deduction_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reason = serializers.CharField(required=False, allow_blank=True)


class RazorpayCreateOrderSerializer(serializers.Serializer):
    rental_id = serializers.PrimaryKeyRelatedField(queryset=Rental.objects.all(), source='rental')


class RazorpayVerifyPaymentSerializer(serializers.Serializer):
    rental_id = serializers.PrimaryKeyRelatedField(queryset=Rental.objects.all(), source='rental')
    razorpay_order_id = serializers.CharField(max_length=150)
    razorpay_payment_id = serializers.CharField(max_length=150)
    razorpay_signature = serializers.CharField(max_length=255)


class StripeCreateIntentSerializer(serializers.Serializer):
    rental_id = serializers.PrimaryKeyRelatedField(queryset=Rental.objects.all(), source='rental')
    currency = serializers.CharField(max_length=10, default='inr')

