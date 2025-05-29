import django_tables2 as tables
from .models import Profile


class ProfileTable(tables.Table):
    """Improved Profile table with basic configuration."""
    
    class Meta:
        model = Profile
        template_name = "django_tables2/bootstrap4.html"  # More widely used
        fields = (
            'date',
            'customer_name', 
            'contact_number',
            'item',
            'price_per_item',
            'quantity',
            'total'
        )
        sequence = fields  # Explicit field order
        order_by = ('-first_name',)  # Default sort (newest first)
        order_by_field = 'sort'
        attrs = {'class': 'table'}  # Basic table class