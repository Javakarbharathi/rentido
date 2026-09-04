from django.contrib import admin
from .models import AuditLogEntry


@admin.register(AuditLogEntry)
class AuditLogEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'actor', 'action', 'target_model', 'target_id', 'timestamp')
    list_filter = ('action', 'target_model', 'timestamp')
    search_fields = ('actor__email', 'target_id', 'target_model')
    readonly_fields = ('actor', 'action', 'target_model', 'target_id', 'details', 'ip_address', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
