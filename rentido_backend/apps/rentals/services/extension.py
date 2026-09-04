import uuid
from decimal import Decimal
from django.utils import timezone
from apps.rentals.models import (
    Rental,
    RentalStatus,
    RentalExtension,
    ExtensionStatus,
    RentalAgreement,
    AgreementAddendum,
    FulfillmentType,
)
from apps.rentals.services.availability import AvailabilityService
from apps.rentals.services.pricing import PricingEngine
from apps.payments.models import (
    Payment,
    PaymentStatus,
    LedgerEntry,
    LedgerEntryType,
    LedgerAccount,
)


class ExtensionService:
    """
    Manages rental extension requests, availability verification, owner approvals,
    financial settlement, and legal agreement addendums.
    """

    @classmethod
    def request_extension(cls, rental, renter, new_end_datetime, reason=""):
        """
        Validates availability, calculates extension fees, and creates a RentalExtension.
        """
        if rental.renter != renter:
            raise ValueError("Only the renter can request an extension.")

        if new_end_datetime <= rental.end_datetime:
            raise ValueError("New end datetime must be later than the current end datetime.")

        if rental.status not in [RentalStatus.CONFIRMED, RentalStatus.READY_FOR_HANDOVER, RentalStatus.ACTIVE]:
            raise ValueError(f"Cannot extend rental in current status: {rental.get_status_display()}.")

        # 1. Check physical asset availability for the extended timeframe
        is_avail, avail_reason = AvailabilityService.check_availability(
            listing=rental.listing,
            start_datetime=rental.end_datetime,
            end_datetime=new_end_datetime,
            exclude_rental_id=rental.id
        )
        if not is_avail:
            raise ValueError(f"Asset is not available for extension: {avail_reason}")

        # 2. Calculate incremental pricing
        pricing = PricingEngine.calculate_pricing(
            listing=rental.listing,
            start_datetime=rental.end_datetime,
            end_datetime=new_end_datetime,
            fulfillment_type=FulfillmentType.SELF_PICKUP
        )

        add_rental = pricing['base_rental_amount']
        add_commission = pricing['platform_commission_amount']
        add_platform_fee = pricing['platform_fee']
        total_extension_cost = add_rental + add_platform_fee

        # 3. Create RentalExtension record
        extension = RentalExtension.objects.create(
            rental=rental,
            previous_end_datetime=rental.end_datetime,
            new_end_datetime=new_end_datetime,
            additional_rental_amount=add_rental,
            additional_commission_amount=add_commission,
            additional_platform_fee=add_platform_fee,
            total_extension_amount=total_extension_cost,
            status=ExtensionStatus.PENDING_APPROVAL,
            reason=reason
        )

        # 4. Update Rental status to EXTENSION_PENDING
        rental.status = RentalStatus.EXTENSION_PENDING
        rental.save()

        return extension

    @classmethod
    def owner_decide(cls, extension, owner, approve=True, rejection_reason=""):
        """
        Owner approves or rejects the requested extension.
        """
        if extension.rental.owner != owner:
            raise ValueError("Only the owner can approve or reject this extension.")

        if extension.status != ExtensionStatus.PENDING_APPROVAL:
            raise ValueError(f"Extension is not pending approval (Current: {extension.status}).")

        if approve:
            extension.is_approved_by_owner = True
            extension.status = ExtensionStatus.APPROVED
            extension.save()
        else:
            extension.status = ExtensionStatus.REJECTED
            extension.rejection_reason = rejection_reason
            extension.save()
            # Revert rental to ACTIVE
            extension.rental.status = RentalStatus.ACTIVE
            extension.rental.save()

        return extension

    @classmethod
    def pay_and_confirm(cls, extension, renter, payment_method="UPI"):
        """
        Processes extension payment, logs ledger records, generates AgreementAddendum,
        and extends rental end_datetime.
        """
        if extension.rental.renter != renter:
            raise ValueError("Only the renter can pay for this extension.")

        if extension.status != ExtensionStatus.APPROVED:
            raise ValueError("Extension must be approved by the owner before payment.")

        rental = extension.rental
        txn_id = f"EXT-TXN-{uuid.uuid4().hex[:10].upper()}"

        # 1. Record Payment
        Payment.objects.create(
            rental=rental,
            payer=renter,
            amount=extension.total_extension_amount,
            transaction_id=txn_id,
            payment_method=payment_method,
            status=PaymentStatus.SUCCESS,
            gateway_response={'type': 'extension_payment', 'status': 'captured'}
        )

        # 2. Record double-entry financial ledger
        # Inflow
        LedgerEntry.objects.create(
            rental=rental,
            entry_type=LedgerEntryType.PAYMENT_RECEIVED,
            debit_account=LedgerAccount.RENTER_BANK_ACCOUNT,
            credit_account=LedgerAccount.ESCROW_INFLOW,
            amount=extension.total_extension_amount,
            description=f"Extension payment for Rental #{rental.id} (+{extension.new_end_datetime.strftime('%d-%b')})",
            reference_id=txn_id
        )

        # Commission
        if extension.additional_commission_amount > Decimal('0.00'):
            LedgerEntry.objects.create(
                rental=rental,
                entry_type=LedgerEntryType.PLATFORM_COMMISSION_EARNED,
                debit_account=LedgerAccount.ESCROW_INFLOW,
                credit_account=LedgerAccount.PLATFORM_REVENUE,
                amount=extension.additional_commission_amount,
                description=f"Platform commission on extension for Rental #{rental.id}",
                reference_id=txn_id
            )

        # Platform Fee
        if extension.additional_platform_fee > Decimal('0.00'):
            LedgerEntry.objects.create(
                rental=rental,
                entry_type=LedgerEntryType.PLATFORM_FEE_EARNED,
                debit_account=LedgerAccount.ESCROW_INFLOW,
                credit_account=LedgerAccount.PLATFORM_REVENUE,
                amount=extension.additional_platform_fee,
                description=f"Extension platform fee for Rental #{rental.id}",
                reference_id=txn_id
            )

        # Owner Payable Liability
        owner_extension_payout = extension.additional_rental_amount - extension.additional_commission_amount
        if owner_extension_payout > Decimal('0.00'):
            LedgerEntry.objects.create(
                rental=rental,
                entry_type=LedgerEntryType.OWNER_PAYABLE_CREDITED,
                debit_account=LedgerAccount.ESCROW_INFLOW,
                credit_account=LedgerAccount.OWNER_PAYABLE,
                amount=owner_extension_payout,
                description=f"Owner extension payout credited for Rental #{rental.id}",
                reference_id=txn_id
            )

        # 3. Extend rental timestamp and update status
        rental.end_datetime = extension.new_end_datetime
        rental.status = RentalStatus.ACTIVE
        rental.save()

        # 4. Mark extension as PAID
        extension.is_paid = True
        extension.status = ExtensionStatus.PAID
        extension.save()

        # 5. Generate Legal Agreement Addendum
        agreement, _ = RentalAgreement.objects.get_or_create(
            rental=rental,
            defaults={
                'agreement_number': f"AGR-{rental.id}-{timezone.now().strftime('%Y%m%d')}",
                'terms_and_conditions': f"Standard Rentido Master Agreement for {rental.listing.title}."
            }
        )

        addendum_num = f"ADD-{rental.id}-{extension.id}-{timezone.now().strftime('%Y%m%d')}"
        AgreementAddendum.objects.create(
            rental_agreement=agreement,
            rental_extension=extension,
            addendum_number=addendum_num,
            extended_until=extension.new_end_datetime,
            additional_amount_paid=extension.total_extension_amount,
            terms_addendum=f"Extension Addendum: Rental period extended until {extension.new_end_datetime.isoformat()}."
        )

        return extension
