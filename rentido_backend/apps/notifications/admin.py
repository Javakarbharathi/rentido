from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'channel', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('channel', 'notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__email', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email_notifications', 'sms_notifications', 'push_notifications', 'marketing_emails')
    search_fields = ('user__email',)
