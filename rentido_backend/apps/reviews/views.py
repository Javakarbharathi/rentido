from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Browse reviews and ratings",
        parameters=[
            OpenApiParameter(name='asset_id', description='Filter reviews for an asset', required=False, type=int),
            OpenApiParameter(name='user_id', description='Filter reviews received by a user', required=False, type=int),
            OpenApiParameter(name='target_type', description='Filter by OWNER, RENTER, ASSET, DRIVER', required=False, type=str),
        ]
    ),
    retrieve=extend_schema(summary="Retrieve review details"),
    create=extend_schema(summary="Submit a review after rental completion")
)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related('rental', 'reviewer', 'reviewee', 'asset')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_queryset(self):
        queryset = self.queryset
        asset_id = self.request.query_params.get('asset_id')
        user_id = self.request.query_params.get('user_id')
        target_type = self.request.query_params.get('target_type')

        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        if user_id:
            queryset = queryset.filter(reviewee_id=user_id)
        if target_type:
            queryset = queryset.filter(target_type=target_type)

        return queryset
