import uuid
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Payment, SecurityDeposit, LedgerEntry, PaymentStatus
from .serializers import (
    PaymentSerializer,
    SecurityDepositSerializer,
    LedgerEntrySerializer,
    InitiatePaymentSerializer,
    SettleDepositSerializer,
)
from .services.ledger import LedgerService
from apps.rentals.models import RentalStatus


@extend_schema_view(
    list=extend_schema(summary="List payments made or received by user"),
    retrieve=extend_schema(summary="Retrieve payment details")
)
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all().select_related('rental', 'payer')
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

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
