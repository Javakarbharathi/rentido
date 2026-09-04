from django.contrib import admin
from .models import Category, CommissionRule


class CommissionRuleInline(admin.TabularInline):
    model = CommissionRule
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CommissionRuleInline]


@admin.register(CommissionRule)
class CommissionRuleAdmin(admin.ModelAdmin):
    list_display = ['category', 'commission_type', 'commission_value', 'priority', 'is_active']
    list_filter = ['commission_type', 'is_active']
    search_fields = ['category__name']
