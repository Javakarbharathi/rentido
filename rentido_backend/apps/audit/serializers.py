from rest_framework import serializers
from .models import AuditLogEntry
from apps.inspections.models import DamageReport
from apps.assets.models import Asset


class AuditLogEntrySerializer(serializers.ModelSerializer):
    actor_email = serializers.ReadOnlyField(source='actor.email')
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLogEntry
        fields = [
            'id', 'actor', 'actor_email', 'action', 'action_display',
            'target_model', 'target_id', 'details', 'ip_address', 'timestamp'
        ]
        read_only_fields = fields


class ArbitrateDisputeSerializer(serializers.Serializer):
    damage_report_id = serializers.PrimaryKeyRelatedField(
        queryset=DamageReport.objects.all(), source='damage_report'
    )
    owner_deduction = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    renter_refund = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    reason = serializers.CharField(required=True, max_length=500)


class VerifyAssetSerializer(serializers.Serializer):
    approved = serializers.BooleanField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True, default='')
