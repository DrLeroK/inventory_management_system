from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from django.utils.text import slugify

from store.models import Item
from accounts.models import Vendor

from django.db import transaction 
from django.db.models import F
from django.core.exceptions import ValidationError


# Create your models here.

class Sale(models.Model):
    """
    Enhanced sales transaction model with:
    - Automatic financial calculations
    - Better data integrity
    - Improved performance
    """
    
    # Transaction timestamp (auto-set on creation)
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Transaction DateTime",
        help_text="When the sale was recorded"
    )
    
    # Customer reference with protection against accidental deletion
    customer = models.ForeignKey(
        'accounts.Customer',  # String reference avoids circular imports
        on_delete=models.PROTECT,  # Prevents deletion if sales exist
        related_name='sales',  # Enables customer.sales.all()
        verbose_name="Customer Account"
    )
    
    # Financial breakdown with validation
    sub_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Amount before taxes"
    )
    
    tax_percentage = models.DecimalField(  # More precise than FloatField
        max_digits=5,  # Supports up to 999.99%
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Tax rate in percentage (e.g., 8.25)"
    )
    
    # Auto-calculated fields (not editable in admin)
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text="Calculated tax amount"
    )
    
    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text="Total including taxes"
    )
    
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Amount received from customer"
    )
    
    amount_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text="Change due to customer"
    )

    class Meta:
        db_table = "sales"  # Maintains same table name
        verbose_name = "Sales Transaction"
        verbose_name_plural = "Sales Transactions"
        ordering = ['-date_added']  # Newest sales first by default
        indexes = [
            models.Index(fields=['date_added']),  # Faster date filtering
            models.Index(fields=['customer']),  # Faster customer lookups
        ]

    def __str__(self):
        return f"TX-{self.id} ({self.date_added.date()}) - ${self.grand_total}"
    
    def save(self, *args, **kwargs):
        if not self.tax_amount and self.tax_percentage and self.sub_total:
            self.tax_amount = self.sub_total * (self.tax_percentage / Decimal('100'))
        if not self.grand_total and self.sub_total:
            self.grand_total = self.sub_total + (self.tax_amount or Decimal('0'))
        if not self.amount_change and self.amount_paid:
            self.amount_change = self.amount_paid - (self.grand_total or Decimal('0'))
        super().save(*args, **kwargs)

    def sum_products(self):
        """Returns total quantity of items sold using efficient SQL aggregation"""
        from django.db.models import Sum
        return self.saledetail_set.aggregate(
            total=Sum('quantity')
        )['total'] or 0  # Returns 0 instead of None if no items

    @property
    def is_fully_paid(self):
        """Check if sale was fully paid (read-only property)"""
        return self.amount_paid >= self.grand_total
    

############################################################

############################################################


class SaleDetail(models.Model):
    """
    Enhanced sale line item with:
    - Data integrity protections
    - Auto-calculated totals
    - Better field definitions
    """
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="details",  # More intuitive name
        verbose_name="Parent Sale"
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,  # Prevent item deletion if used in sales
        verbose_name="Product"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Unit price at time of sale"
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity purchased"
    )
    total_detail = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,  # Auto-calculated
        help_text="Line total (price × quantity)"
    )

    class Meta:
        db_table = "sale_details"
        verbose_name = "Sale Line Item"
        verbose_name_plural = "Sale Line Items"
        indexes = [
            models.Index(fields=['sale']),  # Faster sale lookups
        ]

    def save(self, *args, **kwargs):
        """Auto-calculate line total"""
        self.total_detail = self.price * Decimal(self.quantity)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.item.name} @ {self.price}"


###############################################################

###############################################################


class Purchase(models.Model):
    DELIVERY_STATUS = [
        ('P', 'Pending'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
        ('C', 'Cancelled')
    ]

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="purchases"
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        related_name="vendor_purchases"
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        max_length=100  # Added max length
    )
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )
    status = models.CharField(
        max_length=1,
        choices=DELIVERY_STATUS,
        default='P'
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['vendor']),
            models.Index(fields=['status']),
            models.Index(fields=['order_date']),
        ]

    def clean(self):
        if self.delivery_date and self.delivery_date < self.order_date:
            raise ValidationError("Delivery date cannot be before order date")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.full_clean()
            self.total_cost = self.unit_price * Decimal(self.quantity)
            
            if not self.slug:
                self.slug = self.generate_slug()
                
            if self.status == 'D' and not self.delivery_date:
                self.delivery_date = timezone.now()
                self.item.quantity = F('quantity') + self.quantity
                self.item.save(update_fields=['quantity'])
                
            super().save(*args, **kwargs)

    def generate_slug(self):
        base = f"{self.vendor.name}-{self.item.name}"
        date = self.order_date.strftime('%Y%m%d') if self.order_date else timezone.now().strftime('%Y%m%d')
        return slugify(f"{base}-{date}")[:100]

    def __str__(self):
        return f"PO-{self.id} ({self.item.name})"

    @property
    def status_display(self):
        return dict(self.DELIVERY_STATUS).get(self.status, 'Unknown')
