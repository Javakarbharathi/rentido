from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import Listing, ListingStatus
from .serializers import ListingSerializer, ListingCreateSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Search and browse active rental listings",
        parameters=[
            OpenApiParameter(name='city', description='Filter by city', required=False, type=str),
            OpenApiParameter(name='category', description='Filter by category slug', required=False, type=str),
            OpenApiParameter(name='min_price', description='Minimum rental price', required=False, type=float),
            OpenApiParameter(name='max_price', description='Maximum rental price', required=False, type=float),
            OpenApiParameter(name='pricing_model', description='Filter by HOURLY, DAILY, etc.', required=False, type=str),
            OpenApiParameter(name='search', description='Search title, brand, or description', required=False, type=str),
        ]
    ),
    retrieve=extend_schema(summary="Get rental listing details"),
    create=extend_schema(summary="Create a new rental listing for an owned asset"),
    update=extend_schema(summary="Update rental listing details"),
    destroy=extend_schema(summary="Delete rental listing")
)
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all().select_related(
        'asset', 'asset__owner', 'asset__category'
    ).prefetch_related('asset__media')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ListingCreateSerializer
        return ListingSerializer

    def get_queryset(self):
        queryset = self.queryset
        
        # Public listing views only show PUBLISHED listings
        if self.action in ['list', 'retrieve']:
            queryset = queryset.filter(status=ListingStatus.PUBLISHED)

            # Filtering parameters
            city = self.request.query_params.get('city')
            category_slug = self.request.query_params.get('category')
            min_price = self.request.query_params.get('min_price')
            max_price = self.request.query_params.get('max_price')
            pricing_model = self.request.query_params.get('pricing_model')
            search = self.request.query_params.get('search')

            if city:
                queryset = queryset.filter(city__iexact=city)
            if category_slug:
                queryset = queryset.filter(asset__category__slug=category_slug)
            if min_price:
                queryset = queryset.filter(rental_price__gte=min_price)
            if max_price:
                queryset = queryset.filter(rental_price__lte=max_price)
            if pricing_model:
                queryset = queryset.filter(pricing_model=pricing_model)
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search) |
                    Q(asset__brand__icontains=search) |
                    Q(asset__model_name__icontains=search)
                )

        return queryset

    @extend_schema(
        summary="List all listings owned by the authenticated user",
        responses={200: ListingSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='my-listings')
    def my_listings(self, request):
        user = request.user
        listings = self.queryset.filter(asset__owner=user)
        page = self.paginate_queryset(listings)
        if page is not None:
            serializer = ListingSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ListingSerializer(listings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
