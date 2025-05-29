from django.contrib import admin
from .models import Profile, Customer, Vendor
from django.utils.translation import gettext_lazy as _


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'status', 'role')
    list_filter = ('status', 'role')
    search_fields = ('first_name', 'last_name', 'email', 'user__username')
    readonly_fields = ('slug',)
    fieldsets = (
        (_('User Info'), {
            'fields': ('user', 'first_name', 'last_name', 'email', 'telephone', 'profile_picture')
        }),
        (_('System Settings'), {
            'fields': ('status', 'role', 'slug')
        }),
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'loyalty_points', 'is_premium')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('loyalty_points',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Customer Info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address')
        }),
        (_('Rewards'), {
            'fields': ('loyalty_points',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'website', 'is_active')
    search_fields = ('name', 'phone_number')
    list_filter = ('is_active',)
    readonly_fields = ('slug', 'created_at', 'updated_at')
    fieldsets = (
        (_('Vendor Info'), {
            'fields': ('name', 'phone_number', 'address', 'website')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Metadata'), {
            'fields': ('slug', 'created_at', 'updated_at')
        }),
    )
