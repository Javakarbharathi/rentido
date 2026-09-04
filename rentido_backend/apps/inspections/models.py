from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.rentals.models import Rental


class InspectionType(models.TextChoices):
    PRE_RENTAL = 'PRE_RENTAL', _('Pre-Rental Verification')
    HANDOVER = 'HANDOVER', _('Handover Condition Check')
    RETURN = 'RETURN', _('Return Inspection')
    POST_REPAIR = 'POST_REPAIR', _('Post-Repair Verification')


class ConditionGrade(models.TextChoices):
    EXCELLENT = 'EXCELLENT', _('Excellent / Flawless')
    GOOD = 'GOOD', _('Good / Minor Normal Wear')
    FAIR = 'FAIR', _('Fair / Noticeable Wear')
    DAMAGED = 'DAMAGED', _('Damaged / Missing Accessories')


class Inspection(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='inspections')
    inspection_type = models.CharField(max_length=30, choices=InspectionType.choices)
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='inspections_conducted')
    condition_grade = models.CharField(max_length=20, choices=ConditionGrade.choices, default=ConditionGrade.GOOD)
    checklist_answers = models.JSONField(default=dict, blank=True, help_text="Dynamic checklist items: powers_on, screen_intact, etc.")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Inspection')
        verbose_name_plural = _('Inspections')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_inspection_type_display()} for Rental #{self.rental_id} ({self.get_condition_grade_display()})"


class InspectionMedia(models.Model):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='inspections/photos/')
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inspection Photo #{self.id}"


class DamageSeverity(models.TextChoices):
    LOW = 'LOW', _('Low (Minor scratch/cosmetic)')
    MEDIUM = 'MEDIUM', _('Medium (Repairable functional defect)')
    HIGH = 'HIGH', _('High (Major component failure)')
    CRITICAL = 'CRITICAL', _('Critical (Total loss / irreparable)')


class DamageResponsibility(models.TextChoices):
    PENDING_REVIEW = 'PENDING_REVIEW', _('Pending Review / Assessment')
    RENTER_RESPONSIBILITY = 'RENTER_RESPONSIBILITY', _('Renter Responsibility')
    OWNER_RESPONSIBILITY = 'OWNER_RESPONSIBILITY', _('Owner Responsibility / Pre-existing')
    TRANSPORT_DAMAGE = 'TRANSPORT_DAMAGE', _('Transport / Logistics Damage')
    NORMAL_WEAR = 'NORMAL_WEAR', _('Normal Wear & Tear (No charge)')


class DamageStatus(models.TextChoices):
    REPORTED = 'REPORTED', _('Reported')
    UNDER_REVIEW = 'UNDER_REVIEW', _('Under Review')
    SETTLED = 'SETTLED', _('Settled & Deducted')
    DISPUTED = 'DISPUTED', _('Disputed to Admin')


class DamageReport(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='damage_reports')
    inspection = models.ForeignKey(Inspection, on_delete=models.SET_NULL, null=True, blank=True, related_name='damage_reports')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='damage_reports_filed')
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=DamageSeverity.choices, default=DamageSeverity.MEDIUM)
    responsibility = models.CharField(max_length=30, choices=DamageResponsibility.choices, default=DamageResponsibility.PENDING_REVIEW)
    estimated_repair_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    approved_deduction_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=DamageStatus.choices, default=DamageStatus.REPORTED)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Damage Report')
        verbose_name_plural = _('Damage Reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"Damage Report #{self.id} for Rental #{self.rental_id} ({self.get_severity_display()})"
