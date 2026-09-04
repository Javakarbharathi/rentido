from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.shortcuts import get_object_or_404
from .models import TrustProfile
from .serializers import TrustProfileSerializer, PublicTrustBadgeSerializer


@extend_schema_view(
    list=extend_schema(summary="List trust profiles (Admin only)"),
    retrieve=extend_schema(summary="Retrieve trust profile details"),
)
class TrustProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrustProfile.objects.all().select_related('user').prefetch_related('events')
    serializer_class = TrustProfileSerializer

    def get_permissions(self):
        if self.action in ['retrieve_user_badge']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return self.queryset
        if user.is_authenticated:
            return self.queryset.filter(user=user)
        return self.queryset.none()

    @extend_schema(summary="Retrieve authenticated user's own trust profile and event ledger")
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        profile, _ = TrustProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @extend_schema(summary="Retrieve public trust badge of any user")
    @action(detail=False, methods=['get'], url_path=r'user/(?P<user_id>\d+)')
    def retrieve_user_badge(self, request, user_id=None):
        profile = get_object_or_404(TrustProfile, user_id=user_id)
        serializer = PublicTrustBadgeSerializer(profile)
        return Response(serializer.data)
