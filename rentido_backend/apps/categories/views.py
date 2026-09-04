from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Category, CommissionRule
from .serializers import CategorySerializer, CommissionRuleSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.has_role('SUPER_ADMIN') or request.user.has_role('ADMIN')
        )


@extend_schema_view(
    list=extend_schema(summary="List all categories with subcategories"),
    retrieve=extend_schema(summary="Retrieve category details"),
    create=extend_schema(summary="Create a new category (Admin only)"),
    update=extend_schema(summary="Update category (Admin only)"),
    destroy=extend_schema(summary="Delete category (Admin only)")
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Non-staff users only see active categories
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)
        return queryset


@extend_schema_view(
    list=extend_schema(summary="List commission rules (Admin only)"),
    create=extend_schema(summary="Create commission rule (Admin only)")
)
class CommissionRuleViewSet(viewsets.ModelViewSet):
    queryset = CommissionRule.objects.all().select_related('category')
    serializer_class = CommissionRuleSerializer
    permission_classes = [permissions.IsAdminUser]
