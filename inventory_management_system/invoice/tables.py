import django_tables2 as tables
from django.utils.formats import date_format
from .models import Invoice

class InvoiceTable(tables.Table):
    """Table for displaying invoice records with enhanced formatting."""
    
    date = tables.Column(verbose_name="Date", order_by=("date",))
    price_per_item = tables.Column(verbose_name="Unit Price")
    total = tables.Column(verbose_name="Subtotal")
    
    def render_date(self, value):
        """Format date as short date string."""
        return date_format(value, "SHORT_DATE_FORMAT")
    
    def render_price_per_item(self, value):
        """Format currency values."""
        return f"Ksh{value:,.2f}"
    
    def render_total(self, value):
        """Format currency values."""
        return f"Ksh{value:,.2f}"

    class Meta:
        model = Invoice
        template_name = "django_tables2/bootstrap5.html"  # More modern template
        fields = (
            'date', 
            'customer_name', 
            'item',
            'price_per_item', 
            'quantity', 
            'total'
        )
        attrs = {
            'class': 'table table-hover',  # Bootstrap classes
            'thead': {'class': 'table-light'}
        }
        order_by = '-date'  # Default sort by newest first
        empty_text = "No invoices found"