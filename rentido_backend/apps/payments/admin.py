from django.contrib import admin
from .models import Payment, SecurityDeposit, LedgerEntry


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'rental', 'payer', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'payer__email', 'rental__id']


@admin.register(SecurityDeposit)
class SecurityDepositAdmin(admin.ModelAdmin):
    list_display = ['rental', 'renter', 'total_amount', 'refunded_amount', 'deducted_amount', 'status', 'held_at']
    list_filter = ['status']
    search_fields = ['rental__id', 'renter__email']


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'entry_type', 'debit_account', 'credit_account', 'amount', 'rental', 'reference_id']
    list_filter = ['entry_type', 'debit_account', 'credit_account', 'timestamp']
    search_fields = ['reference_id', 'description', 'rental__id']

    def has_change_permission(self, request, obj=None):
        return False  # Immutable ledger cannot be modified by admin

    def has_delete_permission(self, request, obj=None):
        return False  # Immutable ledger cannot be deleted by admin
