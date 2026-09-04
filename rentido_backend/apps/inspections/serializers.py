from rest_framework import serializers
from .models import (
    Inspection,
    InspectionMedia,
    DamageReport,
    DamageResponsibility,
    DamageStatus,
    InspectionType,
)
from apps.rentals.models import Rental


class InspectionMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionMedia
        fields = ['id', 'image', 'caption', 'created_at']
        read_only_fields = ['id', 'created_at']


class InspectionSerializer(serializers.ModelSerializer):
    photos = InspectionMediaSerializer(many=True, read_only=True)
    inspector_email = serializers.ReadOnlyField(source='inspector.email')
    inspection_type_display = serializers.CharField(source='get_inspection_type_display', read_only=True)
    condition_grade_display = serializers.CharField(source='get_condition_grade_display', read_only=True)

    class Meta:
        model = Inspection
        fields = [
            'id', 'rental', 'inspection_type', 'inspection_type_display',
            'inspector', 'inspector_email', 'condition_grade',
            'condition_grade_display', 'checklist_answers', 'notes',
            'photos', 'created_at'
        ]
        read_only_fields = ['id', 'inspector', 'created_at']


class InspectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = [
            'id', 'rental', 'inspection_type', 'condition_grade',
            'checklist_answers', 'notes'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['inspector'] = self.context['request'].user
        return super().create(validated_data)


class DamageReportSerializer(serializers.ModelSerializer):
    reported_by_email = serializers.ReadOnlyField(source='reported_by.email')
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    responsibility_display = serializers.CharField(source='get_responsibility_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = DamageReport
        fields = [
            'id', 'rental', 'inspection', 'reported_by', 'reported_by_email',
            'description', 'severity', 'severity_display',
            'responsibility', 'responsibility_display',
            'estimated_repair_cost', 'approved_deduction_amount',
            'status', 'status_display', 'resolution_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'reported_by', 'approved_deduction_amount',
            'status', 'resolution_notes', 'created_at', 'updated_at'
        ]


class DamageReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DamageReport
        fields = [
            'id', 'rental', 'inspection', 'description', 'severity',
            'estimated_repair_cost'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['reported_by'] = self.context['request'].user
        return super().create(validated_data)


class ResolveDamageSerializer(serializers.Serializer):
    responsibility = serializers.ChoiceField(choices=DamageResponsibility.choices)
    approved_deduction_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    resolution_notes = serializers.CharField(required=True)
