import django_tables2 as tables
from django.utils.html import format_html
from django.urls import reverse
from .models import Item, Delivery


class ItemTable(tables.Table):
    # Custom column for expired items
    expiring_date = tables.Column(verbose_name="Expiration", order_by=("expiring_date"))
    
    # Make vendor column clickable
    vendor = tables.Column(linkify=lambda record: reverse('vendor-detail', args=[record.vendor.pk]))
    
    class Meta:
        model = Item
        template_name = "django_tables2/bootstrap5.html"  # More modern than Semantic
        fields = (
            'id', 'name', 'category', 'quantity',
            'price', 'expiring_date', 'vendor'
        )
        sequence = fields  # Explicit field order
        order_by_field = 'sort'
        attrs = {
            'class': 'table table-striped table-hover',
            'thead': {'class': 'table-dark'}
        }

    def render_expiring_date(self, value):
        if value:
            return value.strftime("%Y-%m-%d")
        return "N/A"

    def render_selling_price(self, value):
        return f"${value:.2f}"


class DeliveryTable(tables.Table):
    # Custom delivery status column
    status = tables.Column(accessor='is_delivered', verbose_name="Status")
    
    class Meta:
        model = Delivery
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            'id', 'item', 'customer_name', 'phone_number',
            'location', 'date', 'status'
        )
        attrs = {'class': 'table table-sm'}
        order_by = ('-date',)  # Default sort

    def render_status(self, value):
        if value:
            return format_html('<span class="badge bg-success">Delivered</span>')
        return format_html('<span class="badge bg-warning">Pending</span>')

    def render_phone_number(self, value):
        return format_html('<a href="tel:{}">{}</a>', value, value)