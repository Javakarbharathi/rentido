import logging
from django.conf import settings
from apps.notifications.models import (
    Notification,
    NotificationChannel,
    NotificationType,
    NotificationPreference,
)

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """
    Central dispatcher that creates in-app records and triggers asynchronous
    delivery (Email, SMS, Push) via Celery tasks.
    """

    @classmethod
    def send(cls, recipient, notification_type, title, message, data=None, channel=NotificationChannel.IN_APP):
        data = data or {}

        # 1. Always record in-app notification
        notification = Notification.objects.create(
            recipient=recipient,
            channel=channel,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data
        )

        # 2. Check user preferences for additional channels
        prefs, _ = NotificationPreference.objects.get_or_create(user=recipient)

        # 3. Schedule async delivery via Celery task if appropriate
        try:
            from apps.notifications.tasks import send_async_delivery_task
            send_async_delivery_task.delay(
                notification_id=notification.id,
                channel=channel,
                recipient_email=recipient.email,
                title=title,
                message=message
            )
        except Exception as e:
            # If broker is offline during dev/test, gracefully log without failing transaction
            logger.debug(f"Celery task dispatch skipped or deferred: {e}")

        return notification

    @classmethod
    def notify_rental_confirmed(cls, rental):
        return cls.send(
            recipient=rental.renter,
            notification_type=NotificationType.RENTAL_CONFIRMED,
            title=f"Rental #{rental.id} Confirmed!",
            message=f"Your rental for '{rental.listing.title}' has been successfully booked.",
            data={"rental_id": rental.id, "start_datetime": str(rental.start_datetime)}
        )

    @classmethod
    def notify_handover_otp(cls, rental, otp):
        return cls.send(
            recipient=rental.renter,
            notification_type=NotificationType.HANDOVER_OTP,
            title=f"Handover OTP for Rental #{rental.id}",
            message=f"Your secure handover OTP is: {otp}. Share this with the owner/driver upon physical receipt.",
            data={"rental_id": rental.id, "otp": otp}
        )

    @classmethod
    def notify_return_reminder(cls, rental):
        return cls.send(
            recipient=rental.renter,
            notification_type=NotificationType.RETURN_REMINDER,
            title=f"Return Reminder: Rental #{rental.id} Ending Soon",
            message=f"Your rental for '{rental.listing.title}' is scheduled for return at {rental.end_datetime}.",
            data={"rental_id": rental.id, "end_datetime": str(rental.end_datetime)}
        )

    @classmethod
    def notify_overdue(cls, rental, late_hours=0):
        # Notify renter
        cls.send(
            recipient=rental.renter,
            notification_type=NotificationType.OVERDUE_WARNING,
            title=f"URGENT: Rental #{rental.id} is Overdue!",
            message=f"Your rental for '{rental.listing.title}' was due at {rental.end_datetime}. Late return penalties may apply.",
            data={"rental_id": rental.id, "late_hours": late_hours}
        )
        # Notify owner
        return cls.send(
            recipient=rental.owner,
            notification_type=NotificationType.OVERDUE_WARNING,
            title=f"Alert: Rental #{rental.id} Overdue Return",
            message=f"The renter has not yet returned '{rental.listing.title}'. Rentido support is monitoring the return.",
            data={"rental_id": rental.id, "late_hours": late_hours}
        )
