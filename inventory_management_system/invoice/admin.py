from django.contrib import admin
from .models import Invoice


# Register your models here.

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin interface for Invoice model with optimized display"""
    
    fields = (
        ('customer_name', 'contact_number'),
        'item',
        ('price_per_item', 'quantity'),
    )
    
    list_display = (
        'date',
        'customer_name',
        'item_short',
        'quantity',
        'price_per_item',
        'grand_total',
    )
    
    list_display_links = ('date', 'customer_name')
    
    list_filter = (
        'date',
        'item',
    )
    
    search_fields = (
        'customer_name',
        'contact_number',
        'item__name',  # Assuming Item model has a 'name' field
    )
    
    ordering = ('-date',)
    
    def item_short(self, obj):
        """Display shortened item name"""
        return str(obj.item)[:30]  # Show first 30 chars of item name
    item_short.short_description = 'Item'