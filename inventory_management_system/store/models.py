"""
Module: models.py

Contains Django models for handling categories, items, and deliveries.

Classes:
- Category: Represents a category for items.
- Item: Represents an item in the inventory.
- Delivery: Represents a delivery of an item to a customer.

Each class provides specific fields, behaviors, and metadata to support inventory and delivery functionality.
"""

from django.db import models
from django.urls import reverse
from django.forms import model_to_dict
from django_extensions.db.fields import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
# ProcessedImageField: auto-processes (resize, crop, etc.) uploaded images
# ResizeToFill(150,150): forces profile pictures to always be exactly 150×150

from accounts.models import Vendor


class Category(models.Model):
    """
    Represents a category used to group similar items.
    """
    name = models.CharField(max_length=50, verbose_name="Category Name")
    slug = AutoSlugField(unique=True, populate_from='name', verbose_name="Slug")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        """
        Returns a human-readable representation of the category.
        """
        return f"Category: {self.name}"


class Item(models.Model):
    """
    Represents an individual item in the inventory.
    """
    name = models.CharField(max_length=50, verbose_name="Item Name")
    slug = AutoSlugField(unique=True, populate_from='name', verbose_name="Slug")
    description = models.TextField(max_length=256, verbose_name="Item Description")
    image = ProcessedImageField(
        default=None,
        upload_to='item_image/%Y/%m/%d/',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 100},
        blank=True,
        null=True
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Category")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Available Quantity")
    price = models.DecimalField(max_digits=10, decimal_places=2, 
                                validators=[MinValueValidator(0.01)], verbose_name="Unit Price")
    expiring_date = models.DateTimeField(blank=True, null=True, verbose_name="Expiration Date")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, verbose_name="Vendor")

    class Meta:
        ordering = ['name']
        verbose_name = "Item"
        verbose_name_plural = "Items"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        """
        Returns a human-readable representation of the item.
        """
        return f"{self.name} - Category: {self.category.name}, Quantity: {self.quantity}"
    

    def get_absolute_url(self):
        """
        Returns the absolute URL to the item's detail view.
        """
        return reverse('store:product-detail', kwargs={'slug': self.slug})


    def to_json(self):  # Serializes model data to JSON format
        """
        Returns a dictionary representation of the item for serialization.
        """
        product = model_to_dict(self)
        product.update({
            'id': self.id,
            'text': self.name,
            'category': self.category.name,
            'quantity': 1,
            'total_product': 0
        })
        return product


class Delivery(models.Model):
    """
    Represents a delivery of a particular item to a customer.
    """
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Delivered Item")
    customer_name = models.CharField(max_length=30, blank=True, null=True, verbose_name="Customer Name")
    phone_number = PhoneNumberField(blank=True, null=True, verbose_name="Phone Number")
    location = models.CharField(max_length=50, blank=True, null=True, verbose_name="Delivery Location")
    date = models.DateTimeField(verbose_name="Delivery Date")
    is_delivered = models.BooleanField(default=False, verbose_name="Is Delivered")

    class Meta:
        ordering = ['-date']
        verbose_name = "Delivery"
        verbose_name_plural = "Deliveries"
        indexes = [
            models.Index(fields=['item']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        """
        Returns a human-readable representation of the delivery.
        """
        return f"Delivery of {self.item} to {self.customer_name} at {self.location} on {self.date}"
