import django_tables2 as tables
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Sale, Purchase

class SaleTable(tables.Table):
    # Custom column for transaction date formatting
    transaction_date = tables.DateTimeColumn(format='Y-m-d H:i', verbose_name=_("Date"))
    
    # Make customer name clickable
    customer_name = tables.Column(linkify=lambda record: reverse('customer-detail', args=[record.customer.id]))
    
    # Color-coded payment status
    payment_method = tables.Column(verbose_name=_("Payment"))
    
    # Formatted currency columns
    price = tables.Column(verbose_name=_("Unit Price"))
    total_value = tables.Column(verbose_name=_("Total"))
    amount_received = tables.Column(verbose_name=_("Paid"))
    balance = tables.Column(verbose_name=_("Balance"))

    class Meta:
        model = Sale
        template_name = "django_tables2/bootstrap5.html"  # More modern than Semantic
        fields = (
            'item',
            'customer_name',
            'transaction_date',
            'payment_method',
            'quantity',
            'price',
            'total_value',
            'amount_received',
            'balance',
            'profile'
        )
        sequence = fields  # Explicit field order
        attrs = {
            'class': 'table table-striped table-hover',
            'thead': {'class': 'table-light'}
        }
        order_by_field = 'sort'

    def render_price(self, value):
        return f"ETB{value:,.2f}"

    def render_total_value(self, value):
        return f"ETB{value:,.2f}"

    def render_amount_received(self, value):
        return f"ETB{value:,.2f}"

    def render_balance(self, value):
        return format_html(
            '<span class="{}">ETB{:,.2f}</span>',
            'text-danger' if value > 0 else 'text-success',
            abs(value)
        )

    def render_payment_method(self, value):
        css_class = {
            'cash': 'badge bg-success',
            'credit': 'badge bg-warning',
            'mobile': 'badge bg-info'
        }.get(value.lower(), 'badge bg-secondary')
        return format_html('<span class="{}">{}</span>', css_class, value)

class PurchaseTable(tables.Table):
    # Date formatting
    order_date = tables.DateTimeColumn(format='Y-m-d', verbose_name=_("Order Date"))
    delivery_date = tables.DateTimeColumn(format='Y-m-d', verbose_name=_("Delivery Date"))
    
    # Status badge
    delivery_status = tables.Column(verbose_name=_("Status"))
    
    # Currency formatting
    price = tables.Column(verbose_name=_("Unit Price"))
    total_value = tables.Column(verbose_name=_("Total Value"))

    class Meta:
        model = Purchase
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            'item',
            'vendor',
            'order_date',
            'delivery_date',
            'quantity',
            'delivery_status',
            'price',
            'total_value'
        )
        attrs = {
            'class': 'table table-sm table-hover',
            'thead': {'class': 'table-light'}
        }
        order_by = ('-order_date',)  # Default sort
        order_by_field = 'sort'

    def render_price(self, value):
        return f"ETB{value:,.2f}"

    def render_total_value(self, value):
        return f"ETB{value:,.2f}"

    def render_delivery_status(self, value):
        status_map = {
            'P': ('badge bg-warning', 'Pending'),
            'S': ('badge bg-info', 'Shipped'),
            'D': ('badge bg-success', 'Delivered'),
            'C': ('badge bg-danger', 'Cancelled')
        }
        css_class, text = status_map.get(value, ('badge bg-secondary', value))
        return format_html('<span class="{}">{}</span>', css_class, text)