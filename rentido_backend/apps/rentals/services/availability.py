from django.utils import timezone
from apps.rentals.models import Rental, RentalStatus


class AvailabilityService:
    """
    Central service to check availability and prevent double booking of physical assets.
    """
    ACTIVE_RENTAL_STATUSES = [
        RentalStatus.PAYMENT_PENDING,
        RentalStatus.CONFIRMED,
        RentalStatus.READY_FOR_HANDOVER,
        RentalStatus.HANDOVER_IN_PROGRESS,
        RentalStatus.ACTIVE,
        RentalStatus.EXTENSION_PENDING,
        RentalStatus.RETURN_REQUESTED,
        RentalStatus.RETURN_IN_PROGRESS,
        RentalStatus.INSPECTION_PENDING,
    ]

    @classmethod
    def check_availability(cls, listing, start_datetime, end_datetime, exclude_rental_id=None):
        """
        Returns (is_available: bool, reason: str)
        """
        now = timezone.now()

        if start_datetime >= end_datetime:
            return False, "End date and time must be after the start date and time."

        if start_datetime < now:
            return False, "Cannot book a rental period starting in the past."

        # Find any overlapping rentals for the physical asset
        overlapping_rentals = Rental.objects.filter(
            listing__asset=listing.asset,
            status__in=cls.ACTIVE_RENTAL_STATUSES,
            start_datetime__lt=end_datetime,
            end_datetime__gt=start_datetime
        )

        if exclude_rental_id:
            overlapping_rentals = overlapping_rentals.exclude(id=exclude_rental_id)

        if overlapping_rentals.exists():
            conflict = overlapping_rentals.first()
            return False, f"Asset is already reserved from {conflict.start_datetime} to {conflict.end_datetime}."

        return True, "Asset is available for booking."

    @classmethod
    def get_booked_intervals(cls, listing):
        """
        Returns a list of start/end ranges already booked for this listing's asset.
        """
        rentals = Rental.objects.filter(
            listing__asset=listing.asset,
            status__in=cls.ACTIVE_RENTAL_STATUSES,
            end_datetime__gte=timezone.now()
        ).values('start_datetime', 'end_datetime', 'status')
        return list(rentals)
