from django.contrib import admin
from .models import Category, Item, Delivery

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for product categories"""
    list_display = ('name', 'slug')  # Columns shown in list view
    search_fields = ('name',)  # Fields searchable in admin
    ordering = ('name',)  # Default sorting


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin interface for inventory items"""
    list_display = (
        'name', 
        'category', 
        'quantity', 
        'price', 
        'vendor',
        'expiring_date'
    )
    search_fields = ('name', 'category__name', 'vendor__name')  # Search across relations
    list_filter = ('category', 'vendor', 'expiring_date')  # Sidebar filters
    list_editable = ('quantity', 'price')  # Edit directly in list view
    ordering = ('name',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """Admin interface for deliveries"""
    list_display = (
        'item',
        'customer_name',
        'phone_number',
        'delivery_status',  # Custom method
        'date'
    )
    search_fields = ('item__name', 'customer_name')
    list_filter = ('date', 'is_delivered')  # Filter by date/delivery status
    date_hierarchy = 'date'  # Date-based navigation
    ordering = ('-date',)  # Newest first

    def delivery_status(self, obj):
        """Custom column showing delivery status"""
        return "Delivered" if obj.is_delivered else "Pending"
    delivery_status.short_description = 'Status'  # Column header
    