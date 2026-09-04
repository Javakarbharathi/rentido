from django.contrib import admin
from .models import ServiceProvider, ServiceRequest, ServiceCommissionRule


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'category', 'city', 'phone_number', 'rating', 'is_verified', 'is_available']
    list_filter = ['category', 'city', 'is_verified', 'is_available']
    search_fields = ['business_name', 'user__email', 'city']


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'issue_title', 'asset', 'assigned_provider', 'category', 'status', 'final_quote_amount', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['issue_title', 'description', 'asset__name']


@admin.register(ServiceCommissionRule)
class ServiceCommissionRuleAdmin(admin.ModelAdmin):
    list_display = ['category', 'commission_percentage', 'is_active']
