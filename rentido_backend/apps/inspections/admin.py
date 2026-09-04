from django.contrib import admin
from .models import Inspection, InspectionMedia, DamageReport


class InspectionMediaInline(admin.TabularInline):
    model = InspectionMedia
    extra = 1


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'rental', 'inspection_type', 'inspector', 'condition_grade', 'created_at']
    list_filter = ['inspection_type', 'condition_grade', 'created_at']
    search_fields = ['rental__id', 'inspector__email']
    inlines = [InspectionMediaInline]


@admin.register(DamageReport)
class DamageReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'rental', 'reported_by', 'severity', 'responsibility', 'approved_deduction_amount', 'status']
    list_filter = ['severity', 'responsibility', 'status']
    search_fields = ['rental__id', 'reported_by__email']
