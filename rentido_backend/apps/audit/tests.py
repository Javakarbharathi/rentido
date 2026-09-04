from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, RoleChoices, UserRole
from apps.categories.models import Category
from apps.assets.models import Asset, VerificationStatus
from apps.listings.models import Listing, PricingModel, ListingStatus
from apps.rentals.models import Rental, RentalStatus
from apps.payments.models import SecurityDeposit, DepositStatus
from apps.inspections.models import Inspection, DamageReport, DamageStatus
from apps.audit.models import AuditLogEntry, AuditAction
from apps.audit.services.analytics import AuditService, FinancialAnalyticsService


class AuditAndAdminOpsTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='super_admin',
            email='superadmin@rentido.com',
            password='password123'
        )
        UserRole.objects.create(user=self.admin, role=RoleChoices.SUPER_ADMIN, is_active=True)

        self.owner = User.objects.create_user(
            username='audit_owner',
            email='audit_owner@rentido.com',
            password='password123'
        )
        UserRole.objects.create(user=self.owner, role=RoleChoices.OWNER, is_active=True)

        self.renter = User.objects.create_user(
            username='audit_renter',
            email='audit_renter@rentido.com',
            password='password123'
        )
        UserRole.objects.create(user=self.renter, role=RoleChoices.RENTER, is_active=True)

        self.category = Category.objects.create(name='Computers', slug='computers')
        self.asset = Asset.objects.create(
            owner=self.owner,
            category=self.category,
            name='MacBook Pro M3 Max',
            serial_number='APPLE-M3-999',
            replacement_value=Decimal('350000.00'),
            verification_status=VerificationStatus.PENDING
        )
        self.listing = Listing.objects.create(
            asset=self.asset,
            title='MacBook Pro M3 Max 16-inch 64GB',
            description='Ultimate creative workstation',
            rental_price=Decimal('2000.00'),
            pricing_model=PricingModel.DAILY,
            security_deposit=Decimal('20000.00'),
            city='Bangalore',
            pincode='560001',
            status=ListingStatus.PUBLISHED
        )

        now = timezone.now()
        self.rental = Rental.objects.create(
            renter=self.renter,
            owner=self.owner,
            listing=self.listing,
            start_datetime=now - timedelta(days=5),
            end_datetime=now - timedelta(days=2),
            status=RentalStatus.COMPLETED
        )

        self.deposit = SecurityDeposit.objects.create(
            rental=self.rental,
            renter=self.renter,
            total_amount=Decimal('20000.00'),
            status=DepositStatus.HELD
        )

        self.inspection = Inspection.objects.create(
            rental=self.rental,
            inspector=self.owner,
            inspection_type='RETURN',
            condition_grade='FAIR',
            notes='Scratch on display bezel'
        )

        self.damage_report = DamageReport.objects.create(
            inspection=self.inspection,
            rental=self.rental,
            reported_by=self.owner,
            description='Display bezel scratched during rental',
            estimated_repair_cost=Decimal('8000.00'),
            status=DamageStatus.DISPUTED
        )

    def test_financial_overview_admin_access(self):
        """Admin can access financial and escrow audit overview."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin-ops/financial-overview/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('platform_financials', response.data)
        self.assertIn('escrow_reconciliation', response.data)
        self.assertIn('marketplace_operations', response.data)

    def test_financial_overview_forbidden_for_regular_user(self):
        """Non-admin users cannot access financial overview."""
        self.client.force_authenticate(user=self.renter)
        response = self.client.get('/api/admin-ops/financial-overview/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_arbitrate_dispute(self):
        """Admin arbitrates disputed damage report, splitting escrow and logging audit trail."""
        self.client.force_authenticate(user=self.admin)

        payload = {
            'damage_report_id': self.damage_report.id,
            'owner_deduction': '5000.00',
            'renter_refund': '15000.00',
            'reason': 'Admin assessed minor wear and tear; awarded 5000 to owner and 15000 refunded to renter.'
        }
        response = self.client.post('/api/admin-ops/arbitrate-dispute/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'SUCCESS')

        # Verify deposit updated
        self.deposit.refresh_from_db()
        self.assertEqual(self.deposit.status, DepositStatus.PARTIALLY_DEDUCTED)
        self.assertEqual(self.deposit.deducted_amount, Decimal('5000.00'))
        self.assertEqual(self.deposit.refunded_amount, Decimal('15000.00'))

        # Verify audit log entry created
        self.assertTrue(AuditLogEntry.objects.filter(
            action=AuditAction.DISPUTE_ARBITRATED,
            target_model='DamageReport',
            target_id=str(self.damage_report.id)
        ).exists())

    def test_admin_verify_asset(self):
        """Admin approves physical asset verification, changing status to VERIFIED and logging audit."""
        self.client.force_authenticate(user=self.admin)

        payload = {
            'approved': True,
            'reason': 'Invoice and serial number photo verified.'
        }
        response = self.client.post(f'/api/admin-ops/verify-asset/{self.asset.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'SUCCESS')

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.verification_status, VerificationStatus.VERIFIED)

        # Verify audit log
        self.assertTrue(AuditLogEntry.objects.filter(
            action=AuditAction.ASSET_VERIFIED,
            target_model='Asset',
            target_id=str(self.asset.id)
        ).exists())

    def test_audit_log_list_api(self):
        """Admin can list and filter audit trail logs."""
        AuditService.log(
            actor=self.admin,
            action=AuditAction.SYSTEM_CONFIG_UPDATED,
            target_model='System',
            target_id='1',
            details={'updated': 'fee_rules'}
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/audit-logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) >= 1)
