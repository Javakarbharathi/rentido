from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.rentals.models import Rental


class VehicleType(models.TextChoices):
    BIKE = 'BIKE', _('Bike / Scooter (Small items)')
    AUTO = 'AUTO', _('Auto Rickshaw (Medium cargo)')
    CAR = 'CAR', _('Car / Van (Delicate equipment)')
    MINI_TRUCK = 'MINI_TRUCK', _('Mini Truck / Pickup (Furniture/Appliances)')
    TRUCK = 'TRUCK', _('Truck (Heavy cargo / bulk)')
    SPECIAL_TRANSPORT = 'SPECIAL_TRANSPORT', _('Specialized Transport')


class Vehicle(models.Model):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.CharField(max_length=30, choices=VehicleType.choices, default=VehicleType.BIKE)
    registration_number = models.CharField(max_length=50, unique=True)
    make_model = models.CharField(max_length=100, help_text="e.g. Tata Ace, Mahindra Bolero")
    max_payload_kg = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)
    cargo_volume_cbm = models.DecimalField(max_digits=6, decimal_places=2, default=0.50, help_text="Cubic meters capacity")
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')

    def __str__(self):
        return f"{self.make_model} ({self.registration_number}) - {self.get_vehicle_type_display()}"


class DeliveryStatus(models.TextChoices):
    PENDING_DISPATCH = 'PENDING_DISPATCH', _('Pending Driver Dispatch')
    ACCEPTED = 'ACCEPTED', _('Driver Assigned / Accepted')
    ARRIVED_AT_PICKUP = 'ARRIVED_AT_PICKUP', _('Driver Arrived at Pickup')
    PICKED_UP = 'PICKED_UP', _('Asset Picked Up & In-Transit')
    DELIVERED = 'DELIVERED', _('Delivered to Customer')
    CANCELLED = 'CANCELLED', _('Delivery Cancelled')


class DeliveryOrder(models.Model):
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE, related_name='delivery_order')
    assigned_driver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries_assigned'
    )
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    
    # Pickup details (Owner location)
    pickup_address = models.TextField()
    pickup_city = models.CharField(max_length=100)
    pickup_pincode = models.CharField(max_length=20)
    
    # Dropoff details (Renter location)
    dropoff_address = models.TextField()
    dropoff_city = models.CharField(max_length=100)
    dropoff_pincode = models.CharField(max_length=20)

    # 6-digit OTP verification stages
    pickup_otp = models.CharField(max_length=6, blank=True)
    delivery_otp = models.CharField(max_length=6, blank=True)
    
    status = models.CharField(max_length=30, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING_DISPATCH)
    
    # Financial split
    transport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=150.00)
    driver_payout = models.DecimalField(max_digits=10, decimal_places=2, default=135.00)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Delivery Order')
        verbose_name_plural = _('Delivery Orders')
        ordering = ['-created_at']

    def __str__(self):
        return f"Delivery #{self.id} for Rental #{self.rental_id} ({self.get_status_display()})"


class TransportConditionStage(models.TextChoices):
    BEFORE_LOADING = 'BEFORE_LOADING', _('Before Loading (Owner Location)')
    PICKUP_CONFIRMED = 'PICKUP_CONFIRMED', _('Asset Loaded & Secured')
    IN_TRANSIT = 'IN_TRANSIT', _('In-Transit Check')
    DELIVERY_COMPLETED = 'DELIVERY_COMPLETED', _('Unloaded & Handed Over (Customer Location)')


class TransportProof(models.Model):
    delivery_order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE, related_name='transport_proofs')
    stage = models.CharField(max_length=30, choices=TransportConditionStage.choices)
    image = models.ImageField(upload_to='logistics/proofs/')
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Transport Proof')
        verbose_name_plural = _('Transport Proofs')

    def __str__(self):
        return f"Proof for Delivery #{self.delivery_order_id} ({self.get_stage_display()})"


class LogisticsCommissionRule(models.Model):
    vehicle_type = models.CharField(max_length=30, choices=VehicleType.choices, unique=True)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    minimum_fee = models.DecimalField(max_digits=10, decimal_places=2, default=20.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_vehicle_type_display()} — {self.commission_percentage}%"
