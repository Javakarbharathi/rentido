import math
from decimal import Decimal
from django.utils import timezone
from apps.listings.models import PricingModel
from apps.categories.models import CommissionRule
from apps.rentals.models import FulfillmentType


class PricingEngine:
    """
    Central pricing calculation engine for Rentido.
    Computes all components (rental, dynamic commission, platform fee, delivery, deposit)
    and formats them for immutable pricing snapshots.
    """
    DEFAULT_COMMISSION_PERCENT = Decimal('10.00')
    DEFAULT_PLATFORM_FEE = Decimal('50.00')
    DEFAULT_DELIVERY_FEE = Decimal('150.00')

    @classmethod
    def calculate_duration(cls, start_datetime, end_datetime, pricing_model):
        """
        Calculates the billable units according to the listing's pricing model.
        """
        duration = end_datetime - start_datetime
        total_seconds = max(duration.total_seconds(), 0)

        if pricing_model == PricingModel.HOURLY:
            hours = math.ceil(total_seconds / 3600)
            return max(hours, 1)

        elif pricing_model == PricingModel.DAILY:
            days = math.ceil(total_seconds / 86400)
            return max(days, 1)

        elif pricing_model == PricingModel.WEEKLY:
            weeks = math.ceil(total_seconds / (86400 * 7))
            return max(weeks, 1)

        elif pricing_model == PricingModel.MONTHLY:
            months = math.ceil(total_seconds / (86400 * 30))
            return max(months, 1)

        # Default fallback to daily
        return max(math.ceil(total_seconds / 86400), 1)

    @classmethod
    def get_commission_rule(cls, category):
        """
        Finds the highest priority active commission rule for this category.
        """
        now = timezone.now()
        rule = CommissionRule.objects.filter(
            category=category,
            is_active=True
        ).filter(
            effective_from__isnull=True
        ).order_by('-priority', '-created_at').first()
        return rule

    @classmethod
    def calculate_pricing(cls, listing, start_datetime, end_datetime, fulfillment_type=FulfillmentType.SELF_PICKUP):
        """
        Returns a dictionary with complete pricing calculation breakdown.
        """
        units = cls.calculate_duration(start_datetime, end_datetime, listing.pricing_model)
        base_rental_amount = Decimal(units) * listing.rental_price

        # Determine commission rate & amount
        rule = cls.get_commission_rule(listing.asset.category)
        if rule:
            if rule.commission_type == CommissionRule.CommissionType.PERCENTAGE:
                commission_rate = rule.commission_value
                commission_amount = (base_rental_amount * commission_rate / Decimal('100.00'))
            else:
                commission_rate = Decimal('0.00')
                commission_amount = rule.commission_value

            if rule.minimum_fee and commission_amount < rule.minimum_fee:
                commission_amount = rule.minimum_fee
            if rule.maximum_fee and commission_amount > rule.maximum_fee:
                commission_amount = rule.maximum_fee
        else:
            commission_rate = cls.DEFAULT_COMMISSION_PERCENT
            commission_amount = (base_rental_amount * commission_rate / Decimal('100.00'))

        commission_amount = commission_amount.quantize(Decimal('0.01'))

        # Delivery fee
        if fulfillment_type == FulfillmentType.DRIVER_DELIVERY:
            delivery_fee = cls.DEFAULT_DELIVERY_FEE
        else:
            delivery_fee = Decimal('0.00')

        # Platform fee
        platform_fee = cls.DEFAULT_PLATFORM_FEE

        # Security Deposit (Held, not platform revenue)
        security_deposit = listing.security_deposit

        # Total paid by Renter at checkout
        total_amount_paid = (base_rental_amount + platform_fee + delivery_fee + security_deposit).quantize(Decimal('0.01'))

        # Payout due to owner (rental minus platform commission)
        owner_payout_amount = (base_rental_amount - commission_amount).quantize(Decimal('0.01'))

        return {
            'units': units,
            'pricing_model': listing.pricing_model,
            'base_rental_amount': base_rental_amount,
            'platform_commission_rate': commission_rate,
            'platform_commission_amount': commission_amount,
            'platform_fee': platform_fee,
            'delivery_fee': delivery_fee,
            'security_deposit_amount': security_deposit,
            'total_amount_paid': total_amount_paid,
            'owner_payout_amount': owner_payout_amount,
            'raw_calculation': {
                'listing_id': listing.id,
                'listing_title': listing.title,
                'unit_price': str(listing.rental_price),
                'units_count': units,
                'category_id': listing.asset.category.id,
                'calculated_at': timezone.now().isoformat()
            }
        }
