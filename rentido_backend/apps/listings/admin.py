from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'asset', 'rental_price', 'pricing_model', 'security_deposit', 'city', 'status'
    ]
    list_filter = ['status', 'pricing_model', 'city', 'is_delivery_available']
    search_fields = ['title', 'description', 'city', 'asset__name']
