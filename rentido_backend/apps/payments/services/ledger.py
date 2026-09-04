from decimal import Decimal
from django.utils import timezone
from apps.payments.models import (
    LedgerEntry,
    LedgerEntryType,
    LedgerAccount,
    SecurityDeposit,
    DepositStatus,
)


class LedgerService:
    """
    Financial engine managing double-entry ledger records and security deposit escrow.
    """

    @classmethod
    def record_rental_payment(cls, rental, payment):
        """
        Splits customer payment into:
        1. Held Security Deposit (Escrow)
        2. Platform Revenue (Commission + Platform fee + Delivery fee)
        3. Owner Payable Liability
        """
        snapshot = rental.pricing_snapshot

        # 1. Total Customer Payment Inflow
        LedgerEntry.objects.create(
            rental=rental,
            entry_type=LedgerEntryType.PAYMENT_RECEIVED,
            debit_account=LedgerAccount.RENTER_BANK_ACCOUNT,
            credit_account=LedgerAccount.ESCROW_INFLOW,
            amount=snapshot.total_amount_paid,
            description=f"Payment received for Rental #{rental.id}",
            reference_id=payment.transaction_id
        )

        # 2. Security Deposit Hold (Separated from platform revenue)
        if snapshot.security_deposit_amount > Decimal('0.00'):
            LedgerEntry.objects.create(
                rental=rental,
                entry_type=LedgerEntryType.SECURITY_DEPOSIT_HELD,
                debit_account=LedgerAccount.ESCROW_INFLOW,
                credit_account=LedgerAccount.SECURITY_DEPOSIT_ESCROW,
                amount=snapshot.security_deposit_amount,
                description=f"Security deposit held in escrow for Rental #{rental.id}",
                reference_id=payment.transaction_id
            )
            SecurityDeposit.objects.update_or_create(
                rental=rental,
                defaults={
                    'renter': rental.renter,
                    'total_amount': snapshot.security_deposit_amount,
                    'status': DepositStatus.HELD,
                    'held_at': timezone.now()
                }
            )

        # 3. Platform Commission Earned
        if snapshot.platform_commission_amount > Decimal('0.00'):
            LedgerEntry.objects.create(
                rental=rental,
                entry_type=LedgerEntryType.PLATFORM_COMMISSION_EARNED,
                debit_account=LedgerAccount.ESCROW_INFLOW,
                credit_account=LedgerAccount.PLATFORM_REVENUE,
                amount=snapshot.platform_commission_amount,
                description=f"Platform commission for Rental #{rental.id}",
                reference_id=payment.transaction_id
            )

        # 4. Platform Fee Earned
        if snapshot.platform_fee > Decimal('0.00'):
            LedgerEntry.objects.create(
                rental=rental,
                entry_type=LedgerEntryType.PLATFORM_FEE_EARNED,
                debit_account=LedgerAccount.ESCROW_INFLOW,
                credit_account=LedgerAccount.PLATFORM_REVENUE,
                amount=snapshot.platform_fee,
                description=f"Platform service fee for Rental #{rental.id}",
                reference_id=payment.transaction_id
            )

        # 5. Delivery Fee Earned (if applicable)
        if snapshot.delivery_fee > Decimal('0.00'):
            LedgerEntry.objects.create(
                rental=rental,
                entry_type=LedgerEntryType.DELIVERY_FEE_EARNED,
                debit_account=LedgerAccount.ESCROW_INFLOW,
                credit_account=LedgerAccount.PLATFORM_REVENUE,
                amount=snapshot.delivery_fee,
                description=f"Delivery fee for Rental #{rental.id}",
                reference_id=payment.transaction_id
            )

        # 6. Owner Payable Liability
        if snapshot.owner_payout_amount > Decimal('0.00'):
            LedgerEntry.objects.create(
                rental=rental,
                entry_type=LedgerEntryType.OWNER_PAYABLE_CREDITED,
                debit_account=LedgerAccount.ESCROW_INFLOW,
                credit_account=LedgerAccount.OWNER_PAYABLE,
                amount=snapshot.owner_payout_amount,
                description=f"Owner rental proceeds credited for Rental #{rental.id}",
                reference_id=payment.transaction_id
            )

    @classmethod
    def settle_security_deposit(cls, rental, deduction_amount=Decimal('0.00'), reason=""):
        """
        Settles held security deposit: releases un-deducted funds to renter,
        and diverts any damage deduction to owner/repair liability.
        """
        try:
            deposit = rental.security_deposit_record
        except SecurityDeposit.DoesNotExist:
            return None

        if deposit.status != DepositStatus.HELD:
            return deposit

        total = deposit.total_amount
        deduction = min(deduction_amount, total)
        refund = total - deduction

        # Record deduction if damage was assessed
        if deduction > Decimal('0.00'):
            deposit.deducted_amount = deduction
            LedgerEntry.objects.create(
                rental=rental,
                entry_type=LedgerEntryType.DEPOSIT_DEDUCTED,
                debit_account=LedgerAccount.SECURITY_DEPOSIT_ESCROW,
                credit_account=LedgerAccount.OWNER_PAYABLE,
                amount=deduction,
                description=f"Deposit deduction for damage on Rental #{rental.id}: {reason}",
                reference_id=f"DEP-DEDUCT-{rental.id}"
            )

        # Record refund to renter
        if refund > Decimal('0.00'):
            deposit.refunded_amount = refund
            LedgerEntry.objects.create(
                rental=rental,
                entry_type=LedgerEntryType.DEPOSIT_RELEASED,
                debit_account=LedgerAccount.SECURITY_DEPOSIT_ESCROW,
                credit_account=LedgerAccount.RENTER_BANK_ACCOUNT,
                amount=refund,
                description=f"Deposit released to renter for Rental #{rental.id}",
                reference_id=f"DEP-REFUND-{rental.id}"
            )

        if deduction == Decimal('0.00'):
            deposit.status = DepositStatus.RELEASED
        elif deduction == total:
            deposit.status = DepositStatus.FULLY_DEDUCTED
        else:
            deposit.status = DepositStatus.PARTIALLY_DEDUCTED

        deposit.settled_at = timezone.now()
        deposit.notes = reason
        deposit.save()
        return deposit

    @classmethod
    def settle_owner_payout(cls, rental):
        """
        Disburses owner payable funds to owner's bank account.
        """
        snapshot = rental.pricing_snapshot
        payout = snapshot.owner_payout_amount

        # Add any damage deductions credited to owner
        if hasattr(rental, 'security_deposit_record'):
            payout += rental.security_deposit_record.deducted_amount

        entry = LedgerEntry.objects.create(
            rental=rental,
            entry_type=LedgerEntryType.OWNER_PAYOUT_SETTLED,
            debit_account=LedgerAccount.OWNER_PAYABLE,
            credit_account=LedgerAccount.OWNER_BANK_ACCOUNT,
            amount=payout,
            description=f"Payout settled to owner for Rental #{rental.id}",
            reference_id=f"PAYOUT-{rental.id}"
        )
        return entry
