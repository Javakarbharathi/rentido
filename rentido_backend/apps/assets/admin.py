from django.contrib import admin
from .models import Asset, AssetMedia


class AssetMediaInline(admin.TabularInline):
    model = AssetMedia
    extra = 1


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'serial_number', 'owner', 'category', 'verification_status', 'status']
    list_filter = ['verification_status', 'status', 'condition', 'category']
    search_fields = ['name', 'brand', 'model_name', 'serial_number', 'owner__email']
    inlines = [AssetMediaInline]


@admin.register(AssetMedia)
class AssetMediaAdmin(admin.ModelAdmin):
    list_display = ['asset', 'caption', 'is_primary', 'created_at']
