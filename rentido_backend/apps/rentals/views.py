from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Rental, RentalStatus, RentalExtension, ExtensionStatus
from .serializers import (
    RentalSerializer,
    RentalBookingSerializer,
    QuoteRequestSerializer,
    VerifyOTPActionSerializer,
    RentalExtensionSerializer,
    RequestExtensionSerializer,
    OwnerDecideExtensionSerializer,
    PayExtensionSerializer,
)
from .services.pricing import PricingEngine
from .services.extension import ExtensionService


@extend_schema_view(
    list=extend_schema(summary="List user's rentals (as renter or owner)"),
    retrieve=extend_schema(summary="Retrieve rental agreement & pricing details")
)
class RentalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rental.objects.all().select_related(
        'renter', 'owner', 'listing', 'listing__asset', 'pricing_snapshot', 'agreement'
    ).prefetch_related('extensions', 'extensions__addendum')
    serializer_class = RentalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.has_role('SUPER_ADMIN') or user.has_role('ADMIN'):
            return self.queryset
        return self.queryset.filter(Q(renter=user) | Q(owner=user))

    @extend_schema(
        summary="Calculate rental price quote before booking",
        request=QuoteRequestSerializer,
        responses={200: RentalSerializer}
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], url_path='quote')
    def quote(self, request):
        serializer = QuoteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing = serializer.validated_data['listing']
        start_datetime = serializer.validated_data['start_datetime']
        end_datetime = serializer.validated_data['end_datetime']
        fulfillment_type = serializer.validated_data['fulfillment_type']

        pricing = PricingEngine.calculate_pricing(
            listing=listing,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            fulfillment_type=fulfillment_type
        )
        return Response(pricing, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Book a rental reservation",
        request=RentalBookingSerializer,
        responses={201: RentalSerializer}
    )
    @action(detail=False, methods=['post'], url_path='book')
    def book(self, request):
        serializer = RentalBookingSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        rental = serializer.save()
        return Response(RentalSerializer(rental).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Confirm payment (moves rental from PAYMENT_PENDING to CONFIRMED)",
        responses={200: RentalSerializer}
    )
    @action(detail=True, methods=['post'], url_path='confirm-payment')
    def confirm_payment(self, request, pk=None):
        rental = self.get_object()
        if rental.status != RentalStatus.PAYMENT_PENDING:
            return Response(
                {"detail": f"Rental is not in PAYMENT_PENDING state (Current: {rental.status})."},
                status=status.HTTP_400_BAD_REQUEST
            )
        rental.status = RentalStatus.CONFIRMED
        rental.save()
        return Response(RentalSerializer(rental).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Verify Handover OTP (moves status to ACTIVE)",
        request=VerifyOTPActionSerializer,
        responses={200: RentalSerializer}
    )
    @action(detail=True, methods=['post'], url_path='handover')
    def handover(self, request, pk=None):
        rental = self.get_object()
        serializer = VerifyOTPActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data['otp'] != rental.handover_otp:
            return Response({"detail": "Invalid Handover OTP."}, status=status.HTTP_400_BAD_REQUEST)

        rental.status = RentalStatus.ACTIVE
        rental.save()
        return Response(RentalSerializer(rental).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Renter requests return (moves status to RETURN_REQUESTED)",
        responses={200: RentalSerializer}
    )
    @action(detail=True, methods=['post'], url_path='request-return')
    def request_return(self, request, pk=None):
        rental = self.get_object()
        if rental.renter != request.user and not request.user.is_staff:
            return Response({"detail": "Only the renter can request return."}, status=status.HTTP_403_FORBIDDEN)

        rental.status = RentalStatus.RETURN_REQUESTED
        rental.save()
        return Response(RentalSerializer(rental).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Verify Return OTP (moves status to COMPLETED)",
        request=VerifyOTPActionSerializer,
        responses={200: RentalSerializer}
    )
    @action(detail=True, methods=['post'], url_path='return')
    def return_asset(self, request, pk=None):
        rental = self.get_object()
        serializer = VerifyOTPActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data['otp'] != rental.return_otp:
            return Response({"detail": "Invalid Return OTP."}, status=status.HTTP_400_BAD_REQUEST)

        rental.status = RentalStatus.COMPLETED
        rental.save()
        return Response(RentalSerializer(rental).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Renter requests rental extension",
        request=RequestExtensionSerializer,
        responses={201: RentalExtensionSerializer}
    )
    @action(detail=True, methods=['post'], url_path='request-extension')
    def request_extension(self, request, pk=None):
        rental = self.get_object()
        serializer = RequestExtensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            extension = ExtensionService.request_extension(
                rental=rental,
                renter=request.user,
                new_end_datetime=serializer.validated_data['new_end_datetime'],
                reason=serializer.validated_data.get('reason', '')
            )
            return Response(RentalExtensionSerializer(extension).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(summary="List rental extensions"),
    retrieve=extend_schema(summary="Retrieve rental extension details")
)
class RentalExtensionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RentalExtension.objects.all().select_related('rental', 'addendum')
    serializer_class = RentalExtensionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(Q(rental__renter=user) | Q(rental__owner=user))

    @extend_schema(
        summary="Owner approves or rejects rental extension",
        request=OwnerDecideExtensionSerializer,
        responses={200: RentalExtensionSerializer}
    )
    @action(detail=True, methods=['post'], url_path='decide')
    def decide(self, request, pk=None):
        extension = self.get_object()
        serializer = OwnerDecideExtensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            decided = ExtensionService.owner_decide(
                extension=extension,
                owner=request.user,
                approve=serializer.validated_data['approve'],
                rejection_reason=serializer.validated_data.get('rejection_reason', '')
            )
            return Response(RentalExtensionSerializer(decided).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Renter pays for approved extension (confirms addendum)",
        request=PayExtensionSerializer,
        responses={200: RentalExtensionSerializer}
    )
    @action(detail=True, methods=['post'], url_path='pay')
    def pay_extension(self, request, pk=None):
        extension = self.get_object()
        serializer = PayExtensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            confirmed = ExtensionService.pay_and_confirm(
                extension=extension,
                renter=request.user,
                payment_method=serializer.validated_data.get('payment_method', 'UPI')
            )
            return Response(RentalExtensionSerializer(confirmed).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
