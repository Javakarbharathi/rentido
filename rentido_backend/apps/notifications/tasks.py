import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from apps.rentals.models import Rental, RentalStatus
from apps.notifications.models import Notification, NotificationType, NotificationChannel
from apps.trust.services.scoring import TrustScoreEngine
from apps.trust.models import TrustEventType

logger = logging.getLogger(__name__)


@shared_task(name='apps.notifications.tasks.send_async_delivery_task')
def send_async_delivery_task(notification_id, channel, recipient_email, title, message):
    """
    Simulated or provider-backed async delivery (e.g. SendGrid, Twilio, Firebase).
    """
    logger.info(f"[DISPATCH] Delivering notification #{notification_id} via {channel} to {recipient_email}: {title}")
    return {
        "status": "SENT",
        "notification_id": notification_id,
        "channel": channel,
        "recipient": recipient_email
    }


@shared_task(name='apps.notifications.tasks.task_check_upcoming_returns')
def task_check_upcoming_returns():
    """
    Periodic task: Check for active rentals ending within the next 24 hours
    and dispatch return reminders to renters.
    """
    now = timezone.now()
    cutoff = now + timedelta(hours=24)

    upcoming_rentals = Rental.objects.filter(
        status=RentalStatus.ACTIVE,
        end_datetime__gte=now,
        end_datetime__lte=cutoff
    ).select_related('renter', 'listing')

    reminders_sent = 0
    for rental in upcoming_rentals:
        # Check if already sent in last 24h
        already_notified = Notification.objects.filter(
            recipient=rental.renter,
            notification_type=NotificationType.RETURN_REMINDER,
            data__rental_id=rental.id,
            created_at__gte=now - timedelta(hours=24)
        ).exists()

        if not already_notified:
            from apps.notifications.services.dispatcher import NotificationDispatcher
            NotificationDispatcher.notify_return_reminder(rental)
            reminders_sent += 1

    logger.info(f"[PERIODIC] Upcoming return reminders dispatched: {reminders_sent}")
    return {"reminders_sent": reminders_sent}


@shared_task(name='apps.notifications.tasks.task_check_overdue_rentals')
def task_check_overdue_rentals():
    """
    Periodic task: Detect active rentals past end_datetime, trigger trust penalties,
    and alert renter and owner.
    """
    now = timezone.now()
    overdue_rentals = Rental.objects.filter(
        status=RentalStatus.ACTIVE,
        end_datetime__lt=now
    ).select_related('renter', 'owner', 'listing')

    overdue_count = 0
    for rental in overdue_rentals:
        late_hours = round((now - rental.end_datetime).total_seconds() / 3600, 1)

        # Apply late return trust penalty if not already applied
        penalty_applied = Notification.objects.filter(
            recipient=rental.renter,
            notification_type=NotificationType.OVERDUE_WARNING,
            data__rental_id=rental.id
        ).exists()

        if not penalty_applied:
            TrustScoreEngine.record_event(
                user=rental.renter,
                event_type=TrustEventType.LATE_RETURN,
                reference_id=f"RENTAL-LATE-{rental.id}",
                description=f"Rental #{rental.id} overdue by {late_hours} hours"
            )

            from apps.notifications.services.dispatcher import NotificationDispatcher
            NotificationDispatcher.notify_overdue(rental, late_hours=late_hours)
            overdue_count += 1

    logger.info(f"[PERIODIC] Overdue rentals processed: {overdue_count}")
    return {"overdue_processed": overdue_count}


@shared_task(name='apps.notifications.tasks.task_expire_unpaid_rentals')
def task_expire_unpaid_rentals():
    """
    Periodic task: Expire bookings that remained unpaid past threshold (1 hour).
    """
    now = timezone.now()
    threshold = now - timedelta(hours=1)

    unpaid_rentals = Rental.objects.filter(
        status=RentalStatus.PAYMENT_PENDING,
        created_at__lt=threshold
    ).select_related('renter', 'listing')

    expired_count = 0
    for rental in unpaid_rentals:
        rental.status = RentalStatus.CANCELLED
        rental.save(update_fields=['status'])

        Notification.objects.create(
            recipient=rental.renter,
            channel=NotificationChannel.IN_APP,
            notification_type=NotificationType.SYSTEM_ALERT,
            title=f"Booking #{rental.id} Cancelled (Payment Expired)",
            message=f"Your reservation for '{rental.listing.title}' was cancelled because payment was not completed within 1 hour.",
            data={"rental_id": rental.id}
        )
        expired_count += 1

    logger.info(f"[PERIODIC] Unpaid bookings expired: {expired_count}")
    return {"expired_count": expired_count}
