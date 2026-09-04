from decimal import Decimal
from django.db.models import Sum, Count, Q
from django.utils import timezone
from apps.audit.models import AuditLogEntry, AuditAction
from apps.payments.models import (
    LedgerEntry,
    LedgerAccount,
    LedgerEntryType,
    SecurityDeposit,
    DepositStatus,
)
from apps.rentals.models import Rental, RentalStatus
from apps.inspections.models import DamageReport, DamageStatus


class AuditService:
    @classmethod
    def log(cls, actor, action, target_model, target_id, details=None, ip_address=None):
        return AuditLogEntry.objects.create(
            actor=actor,
            action=action,
            target_model=target_model,
            target_id=str(target_id),
            details=details or {},
            ip_address=ip_address
        )

    @classmethod
    def arbitrate_dispute(cls, admin_user, damage_report, owner_deduction, renter_refund, reason=""):
        """
        Final administrative arbitration on disputed security deposit deductions.
        """
        deposit = SecurityDeposit.objects.filter(rental=damage_report.rental).first()
        if not deposit:
            raise ValueError(f"No security deposit record found for Rental #{damage_report.rental_id}")

        total_arbitrated = Decimal(str(owner_deduction)) + Decimal(str(renter_refund))
        if total_arbitrated > deposit.total_amount:
            raise ValueError(f"Arbitrated sum ({total_arbitrated}) cannot exceed held deposit amount ({deposit.total_amount})")

        # Update deposit settlement
        deposit.deducted_amount = Decimal(str(owner_deduction))
        deposit.refunded_amount = Decimal(str(renter_refund))
        if owner_deduction > 0 and renter_refund > 0:
            deposit.status = DepositStatus.PARTIALLY_DEDUCTED
        elif owner_deduction > 0:
            deposit.status = DepositStatus.FULLY_DEDUCTED
        else:
            deposit.status = DepositStatus.RELEASED
        deposit.settled_at = timezone.now()
        deposit.save()

        # Update DamageReport
        damage_report.status = DamageStatus.SETTLED
        damage_report.approved_deduction_amount = Decimal(str(owner_deduction))
        damage_report.resolution_notes = f"Arbitrated by {admin_user.email}: Owner={owner_deduction}, Renter={renter_refund}. Note: {reason}"
        damage_report.save()


        # Audit trail
        cls.log(
            actor=admin_user,
            action=AuditAction.DISPUTE_ARBITRATED,
            target_model='DamageReport',
            target_id=damage_report.id,
            details={
                "rental_id": damage_report.rental_id,
                "owner_deduction": str(owner_deduction),
                "renter_refund": str(renter_refund),
                "reason": reason
            }
        )
        return damage_report


class FinancialAnalyticsService:
    @classmethod
    def get_overview(cls):
        """
        Computes platform-wide real-time financial ledger metrics.
        """
        # Sum commission, platform fees, delivery fees by LedgerEntryType
        commission_total = LedgerEntry.objects.filter(
            entry_type=LedgerEntryType.PLATFORM_COMMISSION_EARNED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        platform_fee_total = LedgerEntry.objects.filter(
            entry_type=LedgerEntryType.PLATFORM_FEE_EARNED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        delivery_fee_total = LedgerEntry.objects.filter(
            entry_type=LedgerEntryType.DELIVERY_FEE_EARNED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        total_platform_revenue = (commission_total + platform_fee_total + delivery_fee_total).quantize(Decimal('0.01'))

        # Escrow metrics
        escrow_held = SecurityDeposit.objects.filter(
            status=DepositStatus.HELD
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        damage_deductions_total = SecurityDeposit.objects.filter(
            status__in=[DepositStatus.FULLY_DEDUCTED, DepositStatus.PARTIALLY_DEDUCTED]
        ).aggregate(total=Sum('deducted_amount'))['total'] or Decimal('0.00')

        deposits_refunded_total = SecurityDeposit.objects.filter(
            status__in=[DepositStatus.RELEASED, DepositStatus.PARTIALLY_DEDUCTED]
        ).aggregate(total=Sum('refunded_amount'))['total'] or Decimal('0.00')

        # Volume metrics
        total_owner_payables = LedgerEntry.objects.filter(
            entry_type=LedgerEntryType.OWNER_PAYABLE_CREDITED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Marketplace operational counts
        rentals_summary = Rental.objects.aggregate(
            total_rentals=Count('id'),
            active_rentals=Count('id', filter=Q(status=RentalStatus.ACTIVE)),
            completed_rentals=Count('id', filter=Q(status=RentalStatus.COMPLETED)),
            disputed_rentals=Count('id', filter=Q(status=RentalStatus.DISPUTED))
        )

        return {
            "platform_financials": {
                "total_platform_revenue": total_platform_revenue,
                "commission_revenue": commission_total,
                "platform_fee_revenue": platform_fee_total,
                "delivery_fee_revenue": delivery_fee_total,
                "total_owner_payables": total_owner_payables,
            },
            "escrow_reconciliation": {
                "active_escrow_held": escrow_held,
                "total_damage_deductions": damage_deductions_total,
                "total_deposits_refunded": deposits_refunded_total,
            },
            "marketplace_operations": rentals_summary,
            "generated_at": timezone.now().isoformat()
        }
