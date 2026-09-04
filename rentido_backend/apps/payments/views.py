import uuid
import json
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view

from decimal import Decimal
from .models import (
    Payment,
    SecurityDeposit,
    LedgerEntry,
    PaymentStatus,
    PaymentMethod,
    LedgerEntryType,
    LedgerAccount,
    DepositStatus,
)
from .serializers import (
    PaymentSerializer,
    SecurityDepositSerializer,
    LedgerEntrySerializer,
    InitiatePaymentSerializer,
    SettleDepositSerializer,
    RazorpayCreateOrderSerializer,
    RazorpayVerifyPaymentSerializer,
    StripeCreateIntentSerializer,
)
from .services.ledger import LedgerService
from .services.gateways import RazorpayGatewayService, StripeGatewayService
from apps.rentals.models import Rental, RentalStatus


@extend_schema_view(
    list=extend_schema(summary="List payments made or received by user"),
    retrieve=extend_schema(summary="Retrieve payment details")
)
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all().select_related('rental', 'payer')
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if getattr(self, 'action', None) in ['razorpay_webhook', 'stripe_webhook']:
            return [permissions.AllowAny()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(Q(payer=user) | Q(rental__owner=user))

    @extend_schema(
        summary="Process rental payment (records ledger entries and confirms rental)",
        request=InitiatePaymentSerializer,
        responses={201: PaymentSerializer}
    )
    @action(detail=False, methods=['post'], url_path='pay')
    def process_payment(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rental = serializer.validated_data['rental']
        method = serializer.validated_data['payment_method']

        if rental.status != RentalStatus.PAYMENT_PENDING:
            return Response(
                {"detail": f"Rental is not in PAYMENT_PENDING state (Current: {rental.status})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        snapshot = rental.pricing_snapshot
        txn_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

        payment = Payment.objects.create(
            rental=rental,
            payer=request.user,
            amount=snapshot.total_amount_paid,
            transaction_id=txn_id,
            payment_method=method,
            status=PaymentStatus.SUCCESS,
            gateway_response={'mode': 'sandbox', 'status': 'captured', 'auth_code': 'OK'}
        )

        # 1. Update Rental Status to CONFIRMED
        rental.status = RentalStatus.CONFIRMED
        rental.save()

        # 2. Record full double-entry financial ledger
        LedgerService.record_rental_payment(rental, payment)

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Create Razorpay Order for Rental Booking",
        request=RazorpayCreateOrderSerializer,
        responses={200: dict}
    )
    @action(detail=False, methods=['post'], url_path='razorpay/create-order')
    def razorpay_create_order(self, request):
        serializer = RazorpayCreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rental = serializer.validated_data['rental']

        if rental.status != RentalStatus.PAYMENT_PENDING:
            return Response(
                {"detail": f"Rental is not in PAYMENT_PENDING state (Current: {rental.status})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order_info = RazorpayGatewayService.create_order(rental, request.user)
            return Response(order_info, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Verify Razorpay cryptographic payment signature and settle booking",
        request=RazorpayVerifyPaymentSerializer,
        responses={200: PaymentSerializer}
    )
    @action(detail=False, methods=['post'], url_path='razorpay/verify')
    def razorpay_verify_payment(self, request):
        serializer = RazorpayVerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rental = serializer.validated_data['rental']
        order_id = serializer.validated_data['razorpay_order_id']
        payment_id = serializer.validated_data['razorpay_payment_id']
        signature = serializer.validated_data['razorpay_signature']

        if rental.status != RentalStatus.PAYMENT_PENDING:
            return Response(
                {"detail": f"Rental is not in PAYMENT_PENDING state (Current: {rental.status})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cryptographic HMAC verification
        is_valid = RazorpayGatewayService.verify_payment_signature(order_id, payment_id, signature)
        if not is_valid:
            return Response(
                {"detail": "Cryptographic signature verification failed. Payment cannot be verified."},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = RazorpayGatewayService.confirm_and_settle(
            rental=rental,
            payer=request.user,
            payment_id=payment_id,
            order_id=order_id,
            signature=signature,
            gateway_payload=request.data,
            method=PaymentMethod.RAZORPAY
        )

        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Razorpay Webhook endpoint for server-to-server events",
        responses={200: dict}
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], url_path='razorpay/webhook')
    def razorpay_webhook(self, request):
        signature = request.headers.get('X-Razorpay-Signature', '')
        payload_bytes = request._request.body if hasattr(request, '_request') else request.body

        # Verify signature
        if not RazorpayGatewayService.verify_webhook_signature(payload_bytes, signature):
            return Response({"detail": "Invalid webhook signature"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_data = json.loads(payload_bytes.decode('utf-8'))
        except Exception:
            return Response({"detail": "Invalid JSON payload"}, status=status.HTTP_400_BAD_REQUEST)

        event = event_data.get('event')
        payload = event_data.get('payload', {})

        if event == 'payment.captured':
            payment_entity = payload.get('payment', {}).get('entity', {})
            order_id = payment_entity.get('order_id')
            payment_id = payment_entity.get('id')
            notes = payment_entity.get('notes', {})
            rental_id = notes.get('rental_id')

            if rental_id:
                try:
                    rental = Rental.objects.get(id=rental_id, status=RentalStatus.PAYMENT_PENDING)
                    RazorpayGatewayService.confirm_and_settle(
                        rental=rental,
                        payer=rental.renter,
                        payment_id=payment_id or f"pay_{uuid.uuid4().hex[:10]}",
                        order_id=order_id or "order_webhook",
                        signature=signature,
                        gateway_payload=payment_entity,
                        method=PaymentMethod.RAZORPAY
                    )
                except Rental.DoesNotExist:
                    pass

        return Response({"status": "handled", "event": event}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create Stripe PaymentIntent for Rental Booking",
        request=StripeCreateIntentSerializer,
        responses={200: dict}
    )
    @action(detail=False, methods=['post'], url_path='stripe/create-intent')
    def stripe_create_intent(self, request):
        serializer = StripeCreateIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rental = serializer.validated_data['rental']
        currency = serializer.validated_data.get('currency', 'inr')

        if rental.status != RentalStatus.PAYMENT_PENDING:
            return Response(
                {"detail": f"Rental is not in PAYMENT_PENDING state (Current: {rental.status})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            intent_data = StripeGatewayService.create_payment_intent(rental, request.user, currency=currency)
            return Response(intent_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Stripe Webhook endpoint for server-to-server events",
        responses={200: dict}
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], url_path='stripe/webhook')
    def stripe_webhook(self, request):
        sig_header = request.headers.get('Stripe-Signature', '')
        payload_bytes = request._request.body if hasattr(request, '_request') else request.body

        event = StripeGatewayService.verify_webhook_signature(payload_bytes, sig_header)
        if not event:
            return Response({"detail": "Invalid Stripe signature"}, status=status.HTTP_400_BAD_REQUEST)

        event_type = event.get('type')
        if event_type == 'payment_intent.succeeded':
            intent = event.get('data', {}).get('object', {})
            metadata = intent.get('metadata', {})
            rental_id = metadata.get('rental_id')
            payment_intent_id = intent.get('id')

            if rental_id:
                try:
                    rental = Rental.objects.get(id=rental_id, status=RentalStatus.PAYMENT_PENDING)
                    RazorpayGatewayService.confirm_and_settle(
                        rental=rental,
                        payer=rental.renter,
                        payment_id=payment_intent_id,
                        order_id=payment_intent_id,
                        signature="stripe_webhook_verified",
                        gateway_payload=intent,
                        method=PaymentMethod.STRIPE
                    )
                except Rental.DoesNotExist:
                    pass

        return Response({"status": "received", "type": event_type}, status=status.HTTP_200_OK)



@extend_schema_view(
    list=extend_schema(summary="List security deposits"),
    retrieve=extend_schema(summary="Retrieve security deposit record")
)
class SecurityDepositViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SecurityDeposit.objects.all().select_related('rental', 'renter')
    serializer_class = SecurityDepositSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(Q(renter=user) | Q(rental__owner=user))

    @extend_schema(
        summary="Settle security deposit release / deduction (Admin / Ops)",
        request=SettleDepositSerializer,
        responses={200: SecurityDepositSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='settle')
    def settle(self, request, pk=None):
        deposit = self.get_object()
        serializer = SettleDepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_deposit = LedgerService.settle_security_deposit(
            rental=deposit.rental,
            deduction_amount=serializer.validated_data['deduction_amount'],
            reason=serializer.validated_data.get('reason', '')
        )
        return Response(SecurityDepositSerializer(updated_deposit).data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(summary="List immutable financial ledger entries"),
    retrieve=extend_schema(summary="Retrieve ledger entry")
)
class LedgerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LedgerEntry.objects.all().select_related('rental')
    serializer_class = LedgerEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(
            Q(rental__renter=user) | Q(rental__owner=user)
        )

    @extend_schema(
        summary="Retrieve owner earnings, payable balance, and escrow statement",
        responses={200: dict}
    )
    @action(detail=False, methods=['get'], url_path='owner-summary')
    def owner_summary(self, request):
        from django.db.models import Sum
        user = request.user
        credited = LedgerEntry.objects.filter(
            rental__owner=user,
            entry_type=LedgerEntryType.OWNER_PAYABLE_CREDITED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        settled = LedgerEntry.objects.filter(
            rental__owner=user,
            entry_type=LedgerEntryType.OWNER_PAYOUT_SETTLED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        pending_payout = credited - settled

        active_deposits = SecurityDeposit.objects.filter(
            rental__owner=user,
            status=DepositStatus.HELD
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        recent_entries = LedgerEntrySerializer(
            LedgerEntry.objects.filter(rental__owner=user)[:10],
            many=True
        ).data

        return Response({
            'total_earnings_credited': str(credited),
            'total_payout_settled': str(settled),
            'pending_payout_balance': str(pending_payout),
            'active_escrow_deposits': str(active_deposits),
            'recent_entries': recent_entries,
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Simulate request payout of pending balance to owner's bank/UPI",
        responses={200: dict}
    )
    @action(detail=False, methods=['post'], url_path='request-payout')
    def request_payout(self, request):
        from django.db.models import Sum
        user = request.user
        credited = LedgerEntry.objects.filter(
            rental__owner=user,
            entry_type=LedgerEntryType.OWNER_PAYABLE_CREDITED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        settled = LedgerEntry.objects.filter(
            rental__owner=user,
            entry_type=LedgerEntryType.OWNER_PAYOUT_SETTLED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        available = credited - settled
        if available <= Decimal('0.00'):
            return Response(
                {"detail": "No pending payable balance available for payout."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create LedgerEntry for settled payout
        latest_rental = Rental.objects.filter(owner=user).order_by('-created_at').first()
        payout_ref = f"PAYOUT-{uuid.uuid4().hex[:8].upper()}"
        LedgerEntry.objects.create(
            rental=latest_rental,
            entry_type=LedgerEntryType.OWNER_PAYOUT_SETTLED,
            debit_account=LedgerAccount.OWNER_PAYABLE,
            credit_account=LedgerAccount.OWNER_BANK_ACCOUNT,
            amount=available,
            description=f"Direct payout disbursed to owner account",
            reference_id=payout_ref
        )

        return Response({
            "message": f"Successfully initiated payout of ₹{available} to registered bank/UPI account.",
            "reference_id": payout_ref,
            "disbursed_amount": str(available),
        }, status=status.HTTP_200_OK)

