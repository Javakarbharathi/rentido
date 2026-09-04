from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'channel', 'channel_display',
            'notification_type', 'notification_type_display',
            'title', 'message', 'data', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = fields


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'email_notifications', 'sms_notifications',
            'push_notifications', 'marketing_emails', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']
