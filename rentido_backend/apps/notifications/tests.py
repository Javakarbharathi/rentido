from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, RoleChoices, UserRole
from apps.categories.models import Category
from apps.assets.models import Asset
from apps.listings.models import Listing, PricingModel, ListingStatus
from apps.rentals.models import Rental, RentalStatus
from apps.notifications.models import (
    Notification,
    NotificationType,
    NotificationChannel,
    NotificationPreference,
)
from apps.notifications.services.dispatcher import NotificationDispatcher
from apps.notifications.tasks import (
    task_check_upcoming_returns,
    task_check_overdue_rentals,
    task_expire_unpaid_rentals,
)
from apps.trust.models import TrustProfile, TrustEventType


class NotificationsAndTasksTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='notif_owner',
            email='notif_owner@rentido.com',
            password='password123'
        )
        UserRole.objects.create(user=self.owner, role=RoleChoices.OWNER, is_active=True)

        self.renter = User.objects.create_user(
            username='notif_renter',
            email='notif_renter@rentido.com',
            password='password123'
        )
        UserRole.objects.create(user=self.renter, role=RoleChoices.RENTER, is_active=True)

        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.asset = Asset.objects.create(
            owner=self.owner,
            category=self.category,
            name='Drone Pro 4K',
            serial_number='DRONE-4K-77',
            replacement_value=Decimal('80000.00')
        )
        self.listing = Listing.objects.create(
            asset=self.asset,
            title='DJI Mavic 3 Pro Cine',
            description='Aerial videography drone',
            rental_price=Decimal('2500.00'),
            pricing_model=PricingModel.DAILY,
            security_deposit=Decimal('15000.00'),
            city='Bangalore',
            pincode='560001',
            status=ListingStatus.PUBLISHED
        )

    def test_notification_dispatcher_creates_records(self):
        """NotificationDispatcher creates valid in-app records and helper methods format messages."""
        notif = NotificationDispatcher.send(
            recipient=self.renter,
            notification_type=NotificationType.SYSTEM_ALERT,
            title="System Maintenance",
            message="Rentido will undergo brief maintenance tonight."
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notif.recipient, self.renter)
        self.assertFalse(notif.is_read)

    def test_notification_mark_read_and_unread_count_api(self):
        """Test listing, counting, and marking notifications as read."""
        NotificationDispatcher.send(
            recipient=self.renter,
            notification_type=NotificationType.SYSTEM_ALERT,
            title="Message 1",
            message="Content 1"
        )
        NotificationDispatcher.send(
            recipient=self.renter,
            notification_type=NotificationType.SYSTEM_ALERT,
            title="Message 2",
            message="Content 2"
        )

        self.client.force_authenticate(user=self.renter)

        # 1. Check unread count
        count_resp = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(count_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(count_resp.data['unread_count'], 2)

        # 2. Mark one read
        first_notif = Notification.objects.filter(recipient=self.renter).first()
        read_resp = self.client.post(f'/api/notifications/{first_notif.id}/mark-read/')
        self.assertEqual(read_resp.status_code, status.HTTP_200_OK)

        count_resp2 = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(count_resp2.data['unread_count'], 1)

        # 3. Mark all read
        all_read_resp = self.client.post('/api/notifications/mark-all-read/')
        self.assertEqual(all_read_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(all_read_resp.data['marked_read_count'], 1)

        count_resp3 = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(count_resp3.data['unread_count'], 0)

    def test_notification_preferences_api(self):
        """User can retrieve and modify delivery channel preferences."""
        self.client.force_authenticate(user=self.renter)

        # Retrieve default preferences
        get_resp = self.client.get('/api/notifications/preferences/')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertTrue(get_resp.data['email_notifications'])
        self.assertFalse(get_resp.data['marketing_emails'])

        # Update preferences
        update_resp = self.client.put('/api/notifications/preferences/', {
            'email_notifications': False,
            'sms_notifications': True,
            'push_notifications': True,
            'marketing_emails': True
        })
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)
        self.assertFalse(update_resp.data['email_notifications'])
        self.assertTrue(update_resp.data['marketing_emails'])

    def test_periodic_task_upcoming_return_reminders(self):
        """Celery periodic task flags rentals ending within 24 hours and dispatches reminders."""
        now = timezone.now()
        rental = Rental.objects.create(
            renter=self.renter,
            owner=self.owner,
            listing=self.listing,
            start_datetime=now - timedelta(days=2),
            end_datetime=now + timedelta(hours=10),  # ending in 10 hours
            status=RentalStatus.ACTIVE
        )

        res = task_check_upcoming_returns()
        self.assertEqual(res['reminders_sent'], 1)

        # Verify notification created
        reminder_notif = Notification.objects.filter(
            recipient=self.renter,
            notification_type=NotificationType.RETURN_REMINDER
        ).first()
        self.assertIsNotNone(reminder_notif)
        self.assertIn("Ending Soon", reminder_notif.title)

        # Second execution does not duplicate
        res2 = task_check_upcoming_returns()
        self.assertEqual(res2['reminders_sent'], 0)

    def test_periodic_task_overdue_rentals_penalties(self):
        """Celery periodic task detects past-due active rentals, applies trust penalties and alerts."""
        now = timezone.now()
        renter_profile, _ = TrustProfile.objects.get_or_create(user=self.renter)
        initial_score = renter_profile.trust_score

        rental = Rental.objects.create(
            renter=self.renter,
            owner=self.owner,
            listing=self.listing,
            start_datetime=now - timedelta(days=3),
            end_datetime=now - timedelta(hours=4),  # 4 hours overdue!
            status=RentalStatus.ACTIVE
        )

        res = task_check_overdue_rentals()
        self.assertEqual(res['overdue_processed'], 1)

        # Verify notifications sent to both renter and owner
        self.assertTrue(Notification.objects.filter(recipient=self.renter, notification_type=NotificationType.OVERDUE_WARNING).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.owner, notification_type=NotificationType.OVERDUE_WARNING).exists())

        # Verify trust penalty deducted 15 points
        renter_profile.refresh_from_db()
        self.assertEqual(renter_profile.trust_score, initial_score - 15)
        self.assertTrue(renter_profile.events.filter(event_type=TrustEventType.LATE_RETURN).exists())

    def test_periodic_task_expire_unpaid_rentals(self):
        """Celery periodic task cancels pending bookings older than 1 hour."""
        now = timezone.now()
        rental = Rental.objects.create(
            renter=self.renter,
            owner=self.owner,
            listing=self.listing,
            start_datetime=now + timedelta(days=1),
            end_datetime=now + timedelta(days=3),
            status=RentalStatus.PAYMENT_PENDING
        )
        # Backdate created_at to 2 hours ago
        Rental.objects.filter(id=rental.id).update(created_at=now - timedelta(hours=2))

        res = task_expire_unpaid_rentals()
        self.assertEqual(res['expired_count'], 1)

        rental.refresh_from_db()
        self.assertEqual(rental.status, RentalStatus.CANCELLED)
