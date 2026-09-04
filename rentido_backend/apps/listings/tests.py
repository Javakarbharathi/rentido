from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.categories.models import Category
from apps.assets.models import Asset, VerificationStatus, AssetStatus
from apps.listings.models import Listing, PricingModel, ListingStatus
from apps.users.models import User, RoleChoices, UserRole


class ListingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Audio', slug='audio')
        self.owner = User.objects.create_user(
            email='soundowner@test.com', username='soundowner', password='Password123!'
        )
        UserRole.objects.create(user=self.owner, role=RoleChoices.OWNER, is_active=True)
        self.asset = Asset.objects.create(
            owner=self.owner,
            category=self.category,
            name='JBL Partybox 310',
            brand='JBL',
            model_name='Partybox 310',
            serial_number='SN-JBL-1122',
            replacement_value='45000.00',
            verification_status=VerificationStatus.VERIFIED,
            status=AssetStatus.AVAILABLE
        )

    def test_owner_can_create_listing(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('listings:listing-list')
        data = {
            'asset_id': self.asset.id,
            'title': 'JBL Partybox 310 Bluetooth Speaker for Rent',
            'description': 'Loud 240W sound with lights, perfect for parties.',
            'rental_price': '1200.00',
            'pricing_model': PricingModel.DAILY,
            'security_deposit': '3000.00',
            'city': 'Chennai',
            'area': 'Anna Nagar',
            'pincode': '600040',
            'is_self_pickup_available': True,
            'is_delivery_available': True
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Listing.objects.filter(asset=self.asset).exists())

    def test_public_can_search_listings(self):
        Listing.objects.create(
            asset=self.asset,
            title='JBL Partybox 310 Bluetooth Speaker',
            description='Loud 240W sound',
            rental_price='1200.00',
            pricing_model=PricingModel.DAILY,
            security_deposit='3000.00',
            city='Chennai',
            pincode='600040',
            status=ListingStatus.PUBLISHED
        )

        url = reverse('listings:listing-list')
        # Search for Chennai
        res = self.client.get(f"{url}?city=Chennai&search=Partybox")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data['results'] if 'results' in res.data else res.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['city'], 'Chennai')
