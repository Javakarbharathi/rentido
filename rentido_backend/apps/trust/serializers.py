from rest_framework import serializers
from .models import TrustProfile, TrustEvent


class TrustEventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)

    class Meta:
        model = TrustEvent
        fields = [
            'id', 'event_type', 'event_type_display', 'score_delta',
            'description', 'reference_id', 'created_at'
        ]
        read_only_fields = fields


class TrustProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    recent_events = serializers.SerializerMethodField()

    class Meta:
        model = TrustProfile
        fields = [
            'id', 'user', 'user_email', 'trust_score', 'tier',
            'tier_display', 'completed_rentals_count', 'dispute_count',
            'updated_at', 'recent_events'
        ]
        read_only_fields = fields

    def get_recent_events(self, obj):
        events = obj.events.all()[:10]
        return TrustEventSerializer(events, many=True).data


class PublicTrustBadgeSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)

    class Meta:
        model = TrustProfile
        fields = ['user', 'user_email', 'trust_score', 'tier', 'tier_display', 'completed_rentals_count']
        read_only_fields = fields
