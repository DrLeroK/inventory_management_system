from django.db import models
from autoslug import AutoSlugField
from django.core.validators import MinValueValidator, RegexValidator

# Create your models here.

# Bill: A bill is a document that records the details of goods or services purchased, 
# including quantities, prices, and total amount payable.
# When you buy stock from a supplier, the bill shows what you got and how much you owe.


class Bill(models.Model):
    """Represents an institutional bill/invoice with payment tracking."""
    
    class PaymentStatus(models.TextChoices):
        UNPAID = 'UN', 'Unpaid'
        PAID = 'PA', 'Paid'
        PARTIAL = 'PR', 'Partially Paid'

    slug = AutoSlugField(
        unique=True, 
        populate_from='date',
        help_text='Automatically generated URL identifier'
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Creation Date'
    )
    institution_name = models.CharField(
        max_length=100,
        verbose_name='Institution',
        help_text='Name of the billed institution'
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        help_text='Contact phone number with country code'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text='Primary contact email'
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text='Full physical address'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed description of charges'
    )
    payment_details = models.CharField(
        max_length=255,
        help_text='Payment method/reference details'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Amount (ETB)',
        help_text='Total amount due'
    )
    status = models.CharField(
        max_length=2,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        verbose_name='Payment Status'
    )

    class Meta:
        ordering = ['-date']
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'

    def __str__(self):
        return f"{self.institution_name} - {self.get_status_display()} (ETB{self.amount})"