from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.assets.models import Asset
from apps.inspections.models import DamageReport


class ServiceCategory(models.TextChoices):
    CAMERA_REPAIR = 'CAMERA_REPAIR', _('Camera & Lens Repair')
    LAPTOP_REPAIR = 'LAPTOP_REPAIR', _('Laptop & Computer Repair')
    BIKE_SERVICE = 'BIKE_SERVICE', _('Bike & Two-Wheeler Service')
    FURNITURE_REPAIR = 'FURNITURE_REPAIR', _('Furniture Restoration & Carpentry')
    GAMING_REPAIR = 'GAMING_REPAIR', _('Gaming Console & Controller Repair')
    CLEANING = 'CLEANING', _('Sanitization & Deep Cleaning')
    MAINTENANCE = 'MAINTENANCE', _('Preventative Maintenance')
    ELECTRONICS = 'ELECTRONICS', _('General Electronics Repair')


class ServiceProvider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_provider_account')
    category = models.CharField(max_length=40, choices=ServiceCategory.choices, default=ServiceCategory.ELECTRONICS)
    business_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    experience_years = models.IntegerField(default=1)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    base_diagnostic_fee = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Service Provider')
        verbose_name_plural = _('Service Providers')
        ordering = ['-rating', '-created_at']

    def __str__(self):
        return f"{self.business_name} ({self.get_category_display()}) — {self.city}"


class ServiceRequestStatus(models.TextChoices):
    PENDING_QUOTE = 'PENDING_QUOTE', _('Pending Provider Quote')
    QUOTED = 'QUOTED', _('Quote Provided (Awaiting Approval)')
    APPROVED_IN_PROGRESS = 'APPROVED_IN_PROGRESS', _('Approved & In-Progress')
    REPAIRED = 'REPAIRED', _('Repaired & Ready for Inspection')
    INSPECTED_CLOSED = 'INSPECTED_CLOSED', _('Inspected & Closed')
    CANCELLED = 'CANCELLED', _('Cancelled')


class ServiceRequest(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='service_requests')
    damage_report = models.ForeignKey(DamageReport, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_requests')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='service_requests_created')
    assigned_provider = models.ForeignKey(ServiceProvider, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
    category = models.CharField(max_length=40, choices=ServiceCategory.choices)
    issue_title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=ServiceRequestStatus.choices, default=ServiceRequestStatus.PENDING_QUOTE)
    
    # Financials
    final_quote_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    provider_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quote_notes = models.TextField(blank=True)
    is_quote_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Service Request')
        verbose_name_plural = _('Service Requests')
        ordering = ['-created_at']

    def __str__(self):
        return f"Service #{self.id}: {self.issue_title} ({self.get_status_display()})"


class ServiceCommissionRule(models.Model):
    category = models.CharField(max_length=40, choices=ServiceCategory.choices, unique=True)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_category_display()} — {self.commission_percentage}%"
