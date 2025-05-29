from django.contrib import admin
from .models import Bill


# Register your models here.

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    """Admin interface for Bill management with improved usability."""
    
    fields = (
        'institution_name',
        ('phone_number', 'email'),
        'address',
        'description',
        'payment_details',
        'amount',
        'status',
    )
    
    list_display = (
        'institution_name',
        'formatted_amount',
        'status',
        'date',
        'contact_info',
    )
    
    list_filter = (
        'status',
        'date',
    )
    
    search_fields = (
        'institution_name',
        'description',
        'payment_details',
    )
    
    ordering = ('-date',)
    
    def formatted_amount(self, obj):
        return f"ETB{obj.amount:,.2f}"
    formatted_amount.short_description = 'Amount'
    
    def contact_info(self, obj):
        return f"{obj.phone_number or ''} {obj.email or ''}".strip()
    contact_info.short_description = 'Contact Info'