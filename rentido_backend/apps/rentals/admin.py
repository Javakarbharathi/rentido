from django.contrib import admin
from .models import (
    Rental,
    RentalPricingSnapshot,
    RentalExtension,
    RentalAgreement,
    AgreementAddendum,
)


class RentalPricingSnapshotInline(admin.StackedInline):
    model = RentalPricingSnapshot
    can_delete = False
    extra = 0


class RentalExtensionInline(admin.TabularInline):
    model = RentalExtension
    extra = 0


class AgreementAddendumInline(admin.StackedInline):
    model = AgreementAddendum
    can_delete = False
    extra = 0


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'renter', 'owner', 'start_datetime', 'end_datetime', 'status', 'fulfillment_type']
    list_filter = ['status', 'fulfillment_type', 'created_at']
    search_fields = ['id', 'listing__title', 'renter__email', 'owner__email', 'handover_otp']
    inlines = [RentalPricingSnapshotInline, RentalExtensionInline]


@admin.register(RentalPricingSnapshot)
class RentalPricingSnapshotAdmin(admin.ModelAdmin):
    list_display = ['rental', 'base_rental_amount', 'platform_commission_amount', 'total_amount_paid', 'created_at']


@admin.register(RentalExtension)
class RentalExtensionAdmin(admin.ModelAdmin):
    list_display = ['id', 'rental', 'previous_end_datetime', 'new_end_datetime', 'status', 'is_approved_by_owner', 'is_paid', 'total_extension_amount']
    list_filter = ['status', 'is_approved_by_owner', 'is_paid']
    inlines = [AgreementAddendumInline]


@admin.register(RentalAgreement)
class RentalAgreementAdmin(admin.ModelAdmin):
    list_display = ['agreement_number', 'rental', 'signed_at', 'is_active']
    search_fields = ['agreement_number', 'rental__id']
    inlines = [AgreementAddendumInline]


@admin.register(AgreementAddendum)
class AgreementAddendumAdmin(admin.ModelAdmin):
    list_display = ['addendum_number', 'rental_agreement', 'extended_until', 'additional_amount_paid', 'created_at']
