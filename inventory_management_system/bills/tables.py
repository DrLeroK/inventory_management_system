import django_tables2 as tables
from .models import Bill
from django.utils.html import format_html
from django.utils.formats import date_format
from django.utils.text import Truncator


class BillTable(tables.Table):
    """Enhanced table for displaying bill records with formatting and better UI."""

    date = tables.Column(verbose_name="Date", order_by=("date",))
    institution_name = tables.Column(verbose_name="Institution")
    phone_number = tables.Column(verbose_name="Phone")
    email = tables.Column(verbose_name="Email")
    address = tables.Column(verbose_name="Address")
    description = tables.Column(verbose_name="Description")
    payment_details = tables.Column(verbose_name="Payment")
    amount = tables.Column(verbose_name="Amount", attrs={
        "td": {"class": "text-end"}
    })
    status = tables.Column(verbose_name="Status", attrs={
        "td": {"class": "text-center"}
    })

    def render_date(self, value):
        return date_format(value, "SHORT_DATE_FORMAT")

    def render_amount(self, value):
        return f"<strong>ETB {value:,.2f}</strong>"

    def render_status(self, value):
        badge_class = {
            'UN': 'bg-warning',
            'PA': 'bg-success',
            'PR': 'bg-info'
        }.get(value, 'bg-secondary')

        return format_html(
            '<span class="badge {} text-white">{}</span>',
            badge_class,
            self.get_status_display(value)
        )

    def render_phone_number(self, value):
        return format_html('<a href="tel:{}">{}</a>', value, value) if value else "-"

    def render_email(self, value):
        return format_html('<a href="mailto:{}">{}</a>', value, value) if value else "-"

    def render_address(self, value):
        return format_html(
            '<span title="{}">{}</span>',
            value,
            Truncator(value).chars(25)
        ) if value else "-"

    def render_description(self, value):
        return format_html(
            '<span title="{}">{}</span>',
            value,
            Truncator(value).chars(30)
        ) if value else "-"

    def render_payment_details(self, value):
        return format_html(
            '<span title="{}">{}</span>',
            value,
            Truncator(value).chars(20)
        )

    def get_status_display(self, value):
        return dict(Bill.PaymentStatus.choices).get(value, value)

    class Meta:
        model = Bill
        template_name = "django_tables2/bootstrap5-responsive.html"
        fields = (
            'date',
            'institution_name',
            'phone_number',
            'email',
            'address',
            'description',
            'payment_details',
            'amount',
            'status',
        )
        attrs = {
            'class': 'table table-hover table-striped align-middle',
            'thead': {'class': 'table-light'},
            'tbody': {'class': 'table-group-divider'}
        }
        order_by_field = 'sort'
        empty_text = "No bill records available"
        per_page = 25
