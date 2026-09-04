from decimal import Decimal
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import (
    ServiceProvider,
    ServiceRequest,
    ServiceRequestStatus,
    ServiceCommissionRule,
)
from .serializers import (
    ServiceProviderSerializer,
    ServiceProviderCreateSerializer,
    ServiceRequestSerializer,
    ServiceRequestCreateSerializer,
    SubmitQuoteSerializer,
    ApproveQuoteSerializer,
)
from apps.assets.models import AssetStatus


@extend_schema_view(
    list=extend_schema(
        summary="Browse and search local service & repair providers",
        parameters=[
            OpenApiParameter(name='category', description='Filter by service category', required=False, type=str),
            OpenApiParameter(name='city', description='Filter by city', required=False, type=str),
        ]
    ),
    retrieve=extend_schema(summary="Retrieve service provider profile"),
    create=extend_schema(summary="Register as a Service Provider")
)
class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all().select_related('user')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceProviderCreateSerializer
        return ServiceProviderSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ['list', 'retrieve'] and not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_verified=True, is_available=True)

        category = self.request.query_params.get('category')
        city = self.request.query_params.get('city')
        if category:
            queryset = queryset.filter(category=category)
        if city:
            queryset = queryset.filter(city__iexact=city)

        return queryset

    @extend_schema(summary="Admin verify service provider", responses={200: ServiceProviderSerializer})
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='verify')
    def verify(self, request, pk=None):
        provider = self.get_object()
        provider.is_verified = True
        provider.save()
        return Response(ServiceProviderSerializer(provider).data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(summary="List service and repair requests"),
    retrieve=extend_schema(summary="Retrieve service request details"),
    create=extend_schema(summary="Create a new service/repair request for an asset")
)
class ServiceRequestViewSet(viewsets.ModelViewSet):
    queryset = ServiceRequest.objects.all().select_related(
        'asset', 'requested_by', 'assigned_provider', 'assigned_provider__user', 'damage_report'
    )
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceRequestCreateSerializer
        elif self.action == 'submit_quote':
            return SubmitQuoteSerializer
        elif self.action == 'approve_quote':
            return ApproveQuoteSerializer
        return ServiceRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(
            Q(requested_by=user) |
            Q(assigned_provider__user=user) |
            Q(asset__owner=user)
        )

    @extend_schema(
        summary="Service provider submits repair quote",
        request=SubmitQuoteSerializer,
        responses={200: ServiceRequestSerializer}
    )
    @action(detail=True, methods=['post'], url_path='submit-quote')
    def submit_quote(self, request, pk=None):
        job = self.get_object()
        serializer = SubmitQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quote_amt = serializer.validated_data['final_quote_amount']
        
        # Calculate platform commission (default 10%)
        rule = ServiceCommissionRule.objects.filter(category=job.category, is_active=True).first()
        comm_pct = rule.commission_percentage if rule else Decimal('10.00')
        platform_comm = (quote_amt * comm_pct / Decimal('100.00')).quantize(Decimal('0.01'))
        provider_cut = (quote_amt - platform_comm).quantize(Decimal('0.01'))

        job.final_quote_amount = quote_amt
        job.platform_commission = platform_comm
        job.provider_payout = provider_cut
        job.quote_notes = serializer.validated_data.get('quote_notes', '')
        job.status = ServiceRequestStatus.QUOTED
        job.save()

        return Response(ServiceRequestSerializer(job).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Asset owner approves repair quote (places asset in MAINTENANCE)",
        request=ApproveQuoteSerializer,
        responses={200: ServiceRequestSerializer}
    )
    @action(detail=True, methods=['post'], url_path='approve-quote')
    def approve_quote(self, request, pk=None):
        job = self.get_object()
        if job.asset.owner != request.user and not request.user.is_staff:
            return Response({"detail": "Only the asset owner can approve repair quotes."}, status=status.HTTP_403_FORBIDDEN)

        job.is_quote_approved = True
        job.status = ServiceRequestStatus.APPROVED_IN_PROGRESS
        job.save()

        # Update physical asset status to MAINTENANCE
        job.asset.status = AssetStatus.MAINTENANCE
        job.asset.save()

        return Response(ServiceRequestSerializer(job).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Service provider marks repair complete",
        responses={200: ServiceRequestSerializer}
    )
    @action(detail=True, methods=['post'], url_path='complete-repair')
    def complete_repair(self, request, pk=None):
        job = self.get_object()
        job.status = ServiceRequestStatus.REPAIRED
        job.save()
        return Response(ServiceRequestSerializer(job).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Owner/Admin post-repair inspection closes job and restores asset to AVAILABLE",
        responses={200: ServiceRequestSerializer}
    )
    @action(detail=True, methods=['post'], url_path='inspect-and-close')
    def inspect_and_close(self, request, pk=None):
        job = self.get_object()
        job.status = ServiceRequestStatus.INSPECTED_CLOSED
        job.save()

        # Asset is now repaired and available for renting again!
        job.asset.status = AssetStatus.AVAILABLE
        job.asset.save()

        return Response(ServiceRequestSerializer(job).data, status=status.HTTP_200_OK)
