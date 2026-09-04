from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'rental', 'reviewer', 'reviewee', 'asset', 'target_type', 'rating', 'created_at')
    list_filter = ('target_type', 'rating', 'created_at')
    search_fields = ('reviewer__email', 'reviewee__email', 'asset__name', 'comment')
    readonly_fields = ('created_at',)
