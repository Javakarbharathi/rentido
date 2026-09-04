from rest_framework import serializers
from .models import Category, CommissionRule


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'parent', 'description', 'icon',
            'is_active', 'subcategories', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class CommissionRuleSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = CommissionRule
        fields = [
            'id', 'category', 'category_name', 'commission_type',
            'commission_value', 'minimum_fee', 'maximum_fee',
            'priority', 'effective_from', 'effective_until', 'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
