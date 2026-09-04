from datetime import timedelta
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.categories.models import Category
from apps.assets.models import Asset, VerificationStatus, AssetStatus
from apps.listings.models import Listing, PricingModel, ListingStatus
from apps.users.models import User, RoleChoices, UserRole
from apps.rentals.models import Rental, RentalStatus, FulfillmentType
from apps.logistics.models import (
    Vehicle,
    VehicleType,
    DeliveryOrder,
    DeliveryStatus,
    TransportConditionStage,
)


class LogisticsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Furniture', slug='furniture')
        self.owner = User.objects.create_user(
            email='furnowner@test.com', username='furnowner', password='Password123!'
        )
        UserRole.objects.create(user=self.owner, role=RoleChoices.OWNER, is_active=True)

        self.renter = User.objects.create_user(
            email='furnrenter@test.com', username='furnrenter', password='Password123!'
        )
        UserRole.objects.create(user=self.renter, role=RoleChoices.RENTER, is_active=True)

        self.driver_user = User.objects.create_user(
            email='driver@test.com', username='driver', password='Password123!'
        )

        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'AdminPass123!')

        self.asset = Asset.objects.create(
            owner=self.owner, category=self.category,
            name='Office Ergonomic Chair', brand='Herman Miller', model_name='Aeron',
            serial_number='SN-HM-AERON-1', replacement_value=Decimal('90000.00'),
            verification_status=VerificationStatus.VERIFIED, status=AssetStatus.AVAILABLE
        )

        self.listing = Listing.objects.create(
            asset=self.asset, title='Herman Miller Aeron Chair', description='Best posture support',
            rental_price=Decimal('1500.00'), pricing_model=PricingModel.DAILY,
            security_deposit=Decimal('5000.00'), city='Bangalore', pincode='560001',
            is_delivery_available=True, status=ListingStatus.PUBLISHED
        )

        now = timezone.now()
        self.rental = Rental.objects.create(
            renter=self.renter, owner=self.owner, listing=self.listing,
            start_datetime=now + timedelta(days=1),
            end_datetime=now + timedelta(days=3),
            fulfillment_type=FulfillmentType.DRIVER_DELIVERY,
            status=RentalStatus.CONFIRMED
        )

    def test_driver_vehicle_registration_auto_assigns_role(self):
        self.client.force_authenticate(user=self.driver_user)
        url = reverse('logistics:vehicle-list')
        data = {
            'vehicle_type': VehicleType.MINI_TRUCK,
            'registration_number': 'KA-01-AB-1234',
            'make_model': 'Tata Ace Gold',
            'max_payload_kg': '750.00',
            'cargo_volume_cbm': '4.50'
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.driver_user.refresh_from_db()
        self.assertTrue(self.driver_user.is_driver)
        self.assertTrue(Vehicle.objects.filter(registration_number='KA-01-AB-1234').exists())

    def test_full_delivery_dispatch_and_otp_flow(self):
        # 1. Driver has registered vehicle
        vehicle = Vehicle.objects.create(
            driver=self.driver_user, vehicle_type=VehicleType.MINI_TRUCK,
            registration_number='KA-02-XY-9999', make_model='Mahindra Bolero Maxi',
            is_verified=True, is_active=True
        )

        # 2. Delivery order created for the rental
        order = DeliveryOrder.objects.create(
            rental=self.rental,
            pickup_address='123 Owner Street', pickup_city='Bangalore', pickup_pincode='560001',
            dropoff_address='456 Renter Avenue', dropoff_city='Bangalore', dropoff_pincode='560025',
            pickup_otp='123456', delivery_otp='654321',
            status=DeliveryStatus.PENDING_DISPATCH
        )

        # 3. Driver accepts delivery
        self.client.force_authenticate(user=self.driver_user)
        accept_url = reverse('logistics:delivery-accept-delivery', kwargs={'pk': order.id})
        res_accept = self.client.post(accept_url, {'vehicle_id': vehicle.id})
        self.assertEqual(res_accept.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, DeliveryStatus.ACCEPTED)
        self.assertEqual(order.assigned_driver, self.driver_user)

        # 4. Driver verifies Pickup OTP at Owner location
        pickup_url = reverse('logistics:delivery-verify-pickup', kwargs={'pk': order.id})
        res_pickup = self.client.post(pickup_url, {'otp': '123456'})
        self.assertEqual(res_pickup.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, DeliveryStatus.PICKED_UP)

        # 5. Driver verifies Delivery OTP at Customer location
        delivery_url = reverse('logistics:delivery-verify-delivery', kwargs={'pk': order.id})
        res_deliv = self.client.post(delivery_url, {'otp': '654321'})
        self.assertEqual(res_deliv.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, DeliveryStatus.DELIVERED)

        # 6. Verify rental status was automatically activated
        self.rental.refresh_from_db()
        self.assertEqual(self.rental.status, RentalStatus.ACTIVE)
