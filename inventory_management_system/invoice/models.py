from django.db import models
from store.models import Item
from django.utils.text import slugify
from django.utils import timezone


# Invoice : Sent by the seller to the buyer.
# It's a formal request for payment, usually with details like 
# what was bought, quantity, price, due date, etc.

class Invoice(models.Model):
    """Represents a customer invoice for purchased items."""

    slug = models.SlugField(
        unique=True,
        blank=True,  # Allow blank initially
        null=False,  # Don't allow null
        default='',  # Set default to avoid migration errors
        help_text="Auto-generated URL identifier"
    )
    date = models.DateTimeField(
        auto_now=True,
        verbose_name='Invoice Date'
    )
    customer_name = models.CharField(
        max_length=100,
        verbose_name='Customer Name'
    )
    contact_number = models.CharField(
        max_length=15,
        verbose_name='Contact Number'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        verbose_name='Purchased Item'
    )
    price_per_item = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Price Per Item (Ksh)'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.00,
        verbose_name='Quantity'
    )
    shipping = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Shipping Cost (Ksh)'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        verbose_name='Subtotal (Ksh)'
    )
    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        verbose_name='Total Amount (Ksh)'
    )

    class Meta:
        ordering = ['-date']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

    def save(self, *args, **kwargs):
        """Calculate totals before saving and generate the slug if empty."""
        self.total = round(self.quantity * self.price_per_item, 2)
        self.grand_total = round(self.total + self.shipping, 2)

        # Generate slug if not already set
        if not self.slug:
            # Use timezone.now() if date isn't set yet
            date_for_slug = self.date if self.date else timezone.now()
            self.slug = self.generate_slug(date_for_slug)

        super().save(*args, **kwargs)

    def generate_slug(self, date):
        """Generate a slug based on the customer name and date."""
        return slugify(f"{self.customer_name}-{date.strftime('%Y-%m-%d-%H%M')}")

    def __str__(self):
        return f"Invoice #{self.slug} for {self.customer_name}"
