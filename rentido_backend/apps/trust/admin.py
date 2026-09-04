from django.contrib import admin
from .models import TrustProfile, TrustEvent


class TrustEventInline(admin.TabularInline):
    model = TrustEvent
    extra = 0
    readonly_fields = ('event_type', 'score_delta', 'description', 'reference_id', 'created_at')
    can_delete = False


@admin.register(TrustProfile)
class TrustProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'trust_score', 'tier', 'completed_rentals_count', 'dispute_count', 'updated_at')
    list_filter = ('tier', 'updated_at')
    search_fields = ('user__email',)
    inlines = [TrustEventInline]


@admin.register(TrustEvent)
class TrustEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'event_type', 'score_delta', 'reference_id', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('profile__user__email', 'reference_id', 'description')
    readonly_fields = ('created_at',)
