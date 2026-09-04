from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.categories.models import Category, CommissionRule
from apps.users.models import User, RoleChoices, UserRole


class CategoryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'AdminPass123!')
        UserRole.objects.create(user=self.admin_user, role=RoleChoices.SUPER_ADMIN, is_active=True)
        self.category = Category.objects.create(name='Cameras', slug='cameras')
        self.subcategory = Category.objects.create(name='DSLR', slug='dslr', parent=self.category)

    def test_public_can_list_categories(self):
        url = reverse('categories:category-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Results contain top-level Cameras with nested DSLR
        data = res.data['results'] if 'results' in res.data else res.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Cameras')
        self.assertEqual(len(data[0]['subcategories']), 1)

    def test_admin_can_create_commission_rule(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('categories:commission-rule-list')
        data = {
            'category': self.category.id,
            'commission_type': 'PERCENTAGE',
            'commission_value': '10.00',
            'minimum_fee': '50.00',
            'priority': 1
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CommissionRule.objects.filter(category=self.category).exists())
