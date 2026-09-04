from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Inspection, InspectionMedia, DamageReport, DamageStatus
from .serializers import (
    InspectionSerializer,
    InspectionCreateSerializer,
    InspectionMediaSerializer,
    DamageReportSerializer,
    DamageReportCreateSerializer,
    ResolveDamageSerializer,
)
from apps.payments.services.ledger import LedgerService


@extend_schema_view(
    list=extend_schema(summary="List inspections for user's rentals"),
    retrieve=extend_schema(summary="Retrieve inspection details"),
    create=extend_schema(summary="Submit an inspection checklist")
)
class InspectionViewSet(viewsets.ModelViewSet):
    queryset = Inspection.objects.all().select_related('rental', 'inspector').prefetch_related('photos')
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'create':
            return InspectionCreateSerializer
        elif self.action == 'upload_photo':
            return InspectionMediaSerializer
        return InspectionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(
            Q(rental__renter=user) | Q(rental__owner=user) | Q(inspector=user)
        )

    @extend_schema(
        summary="Upload condition photo for an inspection",
        request=InspectionMediaSerializer,
        responses={201: InspectionMediaSerializer}
    )
    @action(detail=True, methods=['post'], url_path='upload-photo')
    def upload_photo(self, request, pk=None):
        inspection = self.get_object()
        serializer = InspectionMediaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(inspection=inspection)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(summary="List damage reports"),
    retrieve=extend_schema(summary="Retrieve damage report details"),
    create=extend_schema(summary="File a damage report on a rental")
)
class DamageReportViewSet(viewsets.ModelViewSet):
    queryset = DamageReport.objects.all().select_related('rental', 'inspection', 'reported_by')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return DamageReportCreateSerializer
        elif self.action == 'resolve':
            return ResolveDamageSerializer
        return DamageReportSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(
            Q(rental__renter=user) | Q(rental__owner=user) | Q(reported_by=user)
        )

    @extend_schema(
        summary="Resolve damage report & assess deposit deduction (Admin only)",
        request=ResolveDamageSerializer,
        responses={200: DamageReportSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='resolve')
    def resolve(self, request, pk=None):
        report = self.get_object()
        serializer = ResolveDamageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report.responsibility = serializer.validated_data['responsibility']
        report.approved_deduction_amount = serializer.validated_data['approved_deduction_amount']
        report.resolution_notes = serializer.validated_data['resolution_notes']
        report.status = DamageStatus.SETTLED
        report.save()

        # If a deduction was approved, settle against security deposit in ledger
        if report.approved_deduction_amount > 0:
            LedgerService.settle_security_deposit(
                rental=report.rental,
                deduction_amount=report.approved_deduction_amount,
                reason=f"Damage deduction: {report.resolution_notes}"
            )

        return Response(DamageReportSerializer(report).data, status=status.HTTP_200_OK)
