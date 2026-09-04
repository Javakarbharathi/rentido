from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class RoleChoices(models.TextChoices):
    # Administrative Roles
    SUPER_ADMIN = 'SUPER_ADMIN', _('Super Admin')
    ADMIN = 'ADMIN', _('Admin')
    OPERATIONS_ADMIN = 'OPERATIONS_ADMIN', _('Operations Admin')
    FINANCE_ADMIN = 'FINANCE_ADMIN', _('Finance Admin')
    SUPPORT_ADMIN = 'SUPPORT_ADMIN', _('Support Admin')
    VERIFICATION_ADMIN = 'VERIFICATION_ADMIN', _('Verification Admin')
    
    # Marketplace Participant Roles
    RENTER = 'RENTER', _('Renter')
    OWNER = 'OWNER', _('Owner')
    DRIVER = 'DRIVER', _('Driver')
    SERVICE_PROVIDER = 'SERVICE_PROVIDER', _('Service Provider')


class User(AbstractUser):
    """
    Unified User model for Rentido.
    A single user can hold multiple roles and activate corresponding profiles.
    """
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(_('phone number'), max_length=20, unique=True, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']

    def __str__(self):
        return self.email or self.username

    def has_role(self, role_name):
        return self.roles.filter(role=role_name, is_active=True).exists()

    @property
    def is_renter(self):
        return self.has_role(RoleChoices.RENTER)

    @property
    def is_owner(self):
        return self.has_role(RoleChoices.OWNER)

    @property
    def is_driver(self):
        return self.has_role(RoleChoices.DRIVER)

    @property
    def is_service_provider(self):
        return self.has_role(RoleChoices.SERVICE_PROVIDER)


class UserRole(models.Model):
    """
    Associates a User with a specific Role.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=30, choices=RoleChoices.choices)
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('User Role')
        verbose_name_plural = _('User Roles')
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"


class RenterProfile(models.Model):
    """
    Profile extension for Renters.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='renter_profile')
    emergency_contact = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    kyc_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Renter: {self.user.email}"


class OwnerProfile(models.Model):
    """
    Profile extension for Asset Owners.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    business_name = models.CharField(max_length=150, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Owner: {self.business_name or self.user.email}"
