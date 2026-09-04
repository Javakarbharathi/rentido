from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .models import AuditLogEntry, AuditAction
from .serializers import (
    AuditLogEntrySerializer,
    ArbitrateDisputeSerializer,
    VerifyAssetSerializer,
)
from .services.analytics import AuditService, FinancialAnalyticsService
from apps.assets.models import Asset, VerificationStatus


@extend_schema_view(
    list=extend_schema(
        summary="Browse system audit logs (Admin only)",
        parameters=[
            OpenApiParameter(name='action', description='Filter by action name', required=False, type=str),
            OpenApiParameter(name='target_model', description='Filter by target model name', required=False, type=str),
        ]
    ),
    retrieve=extend_schema(summary="Retrieve audit log detail")
)
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLogEntry.objects.all().select_related('actor')
    serializer_class = AuditLogEntrySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = self.queryset
        action_name = self.request.query_params.get('action')
        target_model = self.request.query_params.get('target_model')

        if action_name:
            queryset = queryset.filter(action=action_name)
        if target_model:
            queryset = queryset.filter(target_model=target_model)

        return queryset


class AdminOperationsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(summary="Platform financial overview, revenue metrics and escrow audit (Admin only)")
    @action(detail=False, methods=['get'], url_path='financial-overview')
    def financial_overview(self, request):
        data = FinancialAnalyticsService.get_overview()
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Arbitrate a disputed damage report and settle security deposit (Admin only)",
        request=ArbitrateDisputeSerializer
    )
    @action(detail=False, methods=['post'], url_path='arbitrate-dispute')
    def arbitrate_dispute(self, request):
        serializer = ArbitrateDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        damage_report = serializer.validated_data['damage_report']
        owner_deduction = serializer.validated_data['owner_deduction']
        renter_refund = serializer.validated_data['renter_refund']
        reason = serializer.validated_data['reason']

        try:
            report = AuditService.arbitrate_dispute(
                admin_user=request.user,
                damage_report=damage_report,
                owner_deduction=owner_deduction,
                renter_refund=renter_refund,
                reason=reason
            )
            return Response({
                "status": "SUCCESS",
                "message": f"Dispute on Rental #{report.rental_id} successfully arbitrated.",
                "damage_report_status": report.status
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"status": "ERROR", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Approve or reject physical asset verification (Admin only)",
        request=VerifyAssetSerializer
    )
    @action(detail=False, methods=['post'], url_path=r'verify-asset/(?P<asset_id>\d+)')
    def verify_asset(self, request, asset_id=None):
        asset = get_object_or_404(Asset, id=asset_id)
        serializer = VerifyAssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        approved = serializer.validated_data['approved']
        reason = serializer.validated_data['reason']

        if approved:
            asset.verification_status = VerificationStatus.VERIFIED
            action_type = AuditAction.ASSET_VERIFIED
        else:
            asset.verification_status = VerificationStatus.REJECTED
            action_type = AuditAction.ASSET_REJECTED

        asset.save(update_fields=['verification_status'])

        AuditService.log(
            actor=request.user,
            action=action_type,
            target_model='Asset',
            target_id=asset.id,
            details={"approved": approved, "reason": reason}
        )

        return Response({
            "status": "SUCCESS",
            "asset_id": asset.id,
            "verification_status": asset.verification_status,
            "message": f"Asset verification updated to {asset.verification_status}."
        }, status=status.HTTP_200_OK)
