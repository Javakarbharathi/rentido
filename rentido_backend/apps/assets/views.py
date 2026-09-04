from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Asset, AssetMedia, VerificationStatus, AssetStatus
from .serializers import (
    AssetSerializer,
    AssetCreateSerializer,
    AssetMediaSerializer,
    AssetVerificationSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="List owner's physical assets (or all if admin)"),
    retrieve=extend_schema(summary="Get physical asset details"),
    create=extend_schema(summary="Register a new physical asset"),
    update=extend_schema(summary="Update physical asset details"),
    destroy=extend_schema(summary="Delete physical asset")
)
class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all().select_related('owner', 'category').prefetch_related('media')
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'create':
            return AssetCreateSerializer
        elif self.action == 'verify':
            return AssetVerificationSerializer
        elif self.action == 'upload_media':
            return AssetMediaSerializer
        return AssetSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.has_role('SUPER_ADMIN') or user.has_role('ADMIN'):
            return self.queryset
        return self.queryset.filter(owner=user)

    @extend_schema(
        summary="Upload media photo for an asset",
        request=AssetMediaSerializer,
        responses={201: AssetMediaSerializer}
    )
    @action(detail=True, methods=['post'], url_path='upload-media')
    def upload_media(self, request, pk=None):
        asset = self.get_object()
        serializer = AssetMediaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(asset=asset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Verify or reject physical asset (Admin only)",
        request=AssetVerificationSerializer,
        responses={200: AssetSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='verify')
    def verify(self, request, pk=None):
        asset = self.get_object()
        serializer = AssetVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        asset.verification_status = serializer.validated_data['verification_status']
        if 'notes' in serializer.validated_data and serializer.validated_data['notes']:
            asset.notes = serializer.validated_data['notes']
        
        # If verified, make asset available
        if asset.verification_status == VerificationStatus.VERIFIED:
            asset.status = AssetStatus.AVAILABLE
            
        asset.save()
        return Response(AssetSerializer(asset).data, status=status.HTTP_200_OK)
