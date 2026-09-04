from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.rentals.models import Rental


class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    SUCCESS = 'SUCCESS', _('Success')
    FAILED = 'FAILED', _('Failed')
    REFUNDED = 'REFUNDED', _('Refunded')


class PaymentMethod(models.TextChoices):
    UPI = 'UPI', _('UPI')
    CREDIT_CARD = 'CREDIT_CARD', _('Credit Card')
    DEBIT_CARD = 'DEBIT_CARD', _('Debit Card')
    NET_BANKING = 'NET_BANKING', _('Net Banking')
    WALLET = 'WALLET', _('Wallet')
    MOCK_GATEWAY = 'MOCK_GATEWAY', _('Mock Gateway (Dev)')


class Payment(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='payments')
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payments_made')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=30, choices=PaymentMethod.choices, default=PaymentMethod.UPI)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    gateway_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.id} — ₹{self.amount} ({self.get_status_display()})"


class DepositStatus(models.TextChoices):
    HELD = 'HELD', _('Held in Escrow')
    RELEASED = 'RELEASED', _('Fully Released to Renter')
    PARTIALLY_DEDUCTED = 'PARTIALLY_DEDUCTED', _('Partially Deducted for Damage')
    FULLY_DEDUCTED = 'FULLY_DEDUCTED', _('Fully Deducted')
    DISPUTED = 'DISPUTED', _('Disputed')


class SecurityDeposit(models.Model):
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE, related_name='security_deposit_record')
    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='held_deposits')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deducted_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, choices=DepositStatus.choices, default=DepositStatus.HELD)
    notes = models.TextField(blank=True)
    held_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Security Deposit')
        verbose_name_plural = _('Security Deposits')

    def __str__(self):
        return f"Deposit for Rental #{self.rental_id} — ₹{self.total_amount} ({self.get_status_display()})"


class LedgerEntryType(models.TextChoices):
    PAYMENT_RECEIVED = 'PAYMENT_RECEIVED', _('Customer Payment Received')
    SECURITY_DEPOSIT_HELD = 'SECURITY_DEPOSIT_HELD', _('Security Deposit Held (Escrow)')
    PLATFORM_COMMISSION_EARNED = 'PLATFORM_COMMISSION_EARNED', _('Platform Commission Earned')
    PLATFORM_FEE_EARNED = 'PLATFORM_FEE_EARNED', _('Platform Fee Earned')
    DELIVERY_FEE_EARNED = 'DELIVERY_FEE_EARNED', _('Delivery Fee Earned')
    OWNER_PAYABLE_CREDITED = 'OWNER_PAYABLE_CREDITED', _('Owner Payable Credited')
    OWNER_PAYOUT_SETTLED = 'OWNER_PAYOUT_SETTLED', _('Owner Payout Settled')
    DEPOSIT_RELEASED = 'DEPOSIT_RELEASED', _('Security Deposit Released to Renter')
    DEPOSIT_DEDUCTED = 'DEPOSIT_DEDUCTED', _('Security Deposit Deducted for Damage')
    REFUND_ISSUED = 'REFUND_ISSUED', _('Refund Issued to Customer')


class LedgerAccount(models.TextChoices):
    ESCROW_INFLOW = 'ESCROW_INFLOW', _('Escrow Clearing Inflow')
    SECURITY_DEPOSIT_ESCROW = 'SECURITY_DEPOSIT_ESCROW', _('Security Deposit Escrow')
    PLATFORM_REVENUE = 'PLATFORM_REVENUE', _('Rentido Platform Revenue')
    OWNER_PAYABLE = 'OWNER_PAYABLE', _('Owner Payable Liability')
    RENTER_BANK_ACCOUNT = 'RENTER_BANK_ACCOUNT', _('Renter Bank/Card')
    OWNER_BANK_ACCOUNT = 'OWNER_BANK_ACCOUNT', _('Owner Bank/UPI')


class LedgerEntry(models.Model):
    """
    Immutable financial transaction ledger enforcing strict double-entry-style accounting.
    """
    rental = models.ForeignKey(Rental, on_delete=models.PROTECT, null=True, blank=True, related_name='ledger_entries')
    entry_type = models.CharField(max_length=40, choices=LedgerEntryType.choices)
    debit_account = models.CharField(max_length=40, choices=LedgerAccount.choices)
    credit_account = models.CharField(max_length=40, choices=LedgerAccount.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    reference_id = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_immutable = models.BooleanField(default=True, editable=False)

    class Meta:
        verbose_name = _('Ledger Entry')
        verbose_name_plural = _('Ledger Entries')
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.get_entry_type_display()}: ₹{self.amount}"
