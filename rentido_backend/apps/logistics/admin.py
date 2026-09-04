from django.contrib import admin
from .models import Vehicle, DeliveryOrder, TransportProof, LogisticsCommissionRule


class TransportProofInline(admin.TabularInline):
    model = TransportProof
    extra = 1


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['registration_number', 'driver', 'vehicle_type', 'make_model', 'max_payload_kg', 'is_verified', 'is_active']
    list_filter = ['vehicle_type', 'is_verified', 'is_active']
    search_fields = ['registration_number', 'make_model', 'driver__email']


@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'rental', 'assigned_driver', 'vehicle', 'status', 'transport_fee', 'driver_payout', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['rental__id', 'assigned_driver__email', 'pickup_city', 'dropoff_city']
    inlines = [TransportProofInline]


@admin.register(LogisticsCommissionRule)
class LogisticsCommissionRuleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_type', 'commission_percentage', 'minimum_fee', 'is_active']
    list_filter = ['is_active']
