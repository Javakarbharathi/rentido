from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Vehicle, DeliveryOrder, TransportProof, DeliveryStatus
from .serializers import (
    VehicleSerializer,
    VehicleCreateSerializer,
    DeliveryOrderSerializer,
    AcceptDeliverySerializer,
    VerifyDeliveryOTPSerializer,
    TransportProofSerializer,
)
from apps.rentals.models import RentalStatus


@extend_schema_view(
    list=extend_schema(summary="List registered vehicles"),
    create=extend_schema(summary="Register a transport vehicle (auto-activates Driver role)")
)
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().select_related('driver')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return VehicleCreateSerializer
        return VehicleSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(driver=user)

    @extend_schema(summary="Admin verify vehicle", responses={200: VehicleSerializer})
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='verify')
    def verify(self, request, pk=None):
        vehicle = self.get_object()
        vehicle.is_verified = True
        vehicle.save()
        return Response(VehicleSerializer(vehicle).data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(summary="List delivery orders"),
    retrieve=extend_schema(summary="Retrieve delivery order details")
)
class DeliveryOrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DeliveryOrder.objects.all().select_related(
        'rental', 'assigned_driver', 'vehicle'
    ).prefetch_related('transport_proofs')
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'upload_proof':
            return TransportProofSerializer
        return DeliveryOrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset

        # Drivers see available unassigned orders + their own assigned orders
        # Renters & Owners see orders related to their rentals
        return self.queryset.filter(
            Q(status=DeliveryStatus.PENDING_DISPATCH) |
            Q(assigned_driver=user) |
            Q(rental__renter=user) |
            Q(rental__owner=user)
        )

    @extend_schema(
        summary="Driver accepts delivery dispatch",
        request=AcceptDeliverySerializer,
        responses={200: DeliveryOrderSerializer}
    )
    @action(detail=True, methods=['post'], url_path='accept')
    def accept_delivery(self, request, pk=None):
        order = self.get_object()
        if order.status != DeliveryStatus.PENDING_DISPATCH:
            return Response({"detail": "This delivery order is already assigned or completed."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AcceptDeliverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.validated_data['vehicle']

        if vehicle.driver != request.user:
            return Response({"detail": "You can only assign your own vehicle."}, status=status.HTTP_403_FORBIDDEN)

        order.assigned_driver = request.user
        order.vehicle = vehicle
        order.status = DeliveryStatus.ACCEPTED
        order.save()
        return Response(DeliveryOrderSerializer(order).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Verify Pickup OTP at Owner location (moves status to PICKED_UP)",
        request=VerifyDeliveryOTPSerializer,
        responses={200: DeliveryOrderSerializer}
    )
    @action(detail=True, methods=['post'], url_path='verify-pickup')
    def verify_pickup(self, request, pk=None):
        order = self.get_object()
        if order.assigned_driver != request.user and not request.user.is_staff:
            return Response({"detail": "Only the assigned driver can verify pickup."}, status=status.HTTP_403_FORBIDDEN)

        serializer = VerifyDeliveryOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data['otp'] != order.pickup_otp:
            return Response({"detail": "Invalid Pickup OTP."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = DeliveryStatus.PICKED_UP
        order.save()
        return Response(DeliveryOrderSerializer(order).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Upload photographic transport condition proof",
        request=TransportProofSerializer,
        responses={201: TransportProofSerializer}
    )
    @action(detail=True, methods=['post'], url_path='upload-proof')
    def upload_proof(self, request, pk=None):
        order = self.get_object()
        serializer = TransportProofSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(delivery_order=order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Verify Delivery OTP at Customer location (completes delivery & activates rental)",
        request=VerifyDeliveryOTPSerializer,
        responses={200: DeliveryOrderSerializer}
    )
    @action(detail=True, methods=['post'], url_path='verify-delivery')
    def verify_delivery(self, request, pk=None):
        order = self.get_object()
        if order.assigned_driver != request.user and not request.user.is_staff:
            return Response({"detail": "Only the assigned driver can verify delivery."}, status=status.HTTP_403_FORBIDDEN)

        serializer = VerifyDeliveryOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data['otp'] != order.delivery_otp:
            return Response({"detail": "Invalid Delivery OTP."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = DeliveryStatus.DELIVERED
        order.save()

        # Automatically transition the Rental to ACTIVE upon successful customer delivery
        order.rental.status = RentalStatus.ACTIVE
        order.rental.save()

        return Response(DeliveryOrderSerializer(order).data, status=status.HTTP_200_OK)
