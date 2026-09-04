from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserRole, RenterProfile, OwnerProfile


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1


class RenterProfileInline(admin.StackedInline):
    model = RenterProfile
    can_delete = False
    extra = 0


class OwnerProfileInline(admin.StackedInline):
    model = OwnerProfile
    can_delete = False
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserRoleInline, RenterProfileInline, OwnerProfileInline]
    list_display = ['email', 'username', 'is_staff', 'is_email_verified', 'created_at']
    search_fields = ['email', 'username', 'phone_number']
    ordering = ['-created_at']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active', 'assigned_at']
    list_filter = ['role', 'is_active']
    search_fields = ['user__email']


@admin.register(RenterProfile)
class RenterProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'kyc_verified', 'created_at']
    list_filter = ['kyc_verified']
    search_fields = ['user__email', 'city']


@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name', 'is_verified', 'rating', 'created_at']
    list_filter = ['is_verified']
    search_fields = ['user__email', 'business_name']
