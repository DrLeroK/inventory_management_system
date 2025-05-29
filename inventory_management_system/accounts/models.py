from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# Helps you raise custom validation errors when saving a model
from django.core.exceptions import ValidationError

from django.utils.text import slugify
# Converts text into a URL-friendly "slug" (lowercase, hyphens instead of spaces)

from django.urls import reverse

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
# ProcessedImageField: auto-processes (resize, crop, etc.) uploaded images
# ResizeToFill(150,150): forces profile pictures to always be exactly 150×150

from phonenumber_field.modelfields import PhoneNumberField
import uuid
# Python’s built-in module to generate unique random IDs


class Profile(models.Model):
    class Status(models.TextChoices):
        INACTIVE = 'INA', _('Inactive')
        ACTIVE = 'A', _('Active')
        ON_LEAVE = 'OL', _('On leave')
    
    class Role(models.TextChoices):
        OPERATIVE = 'OP', _('Operative')
        EXECUTIVE = 'EX', _('Executive')
        ADMIN = 'AD', _('Admin')

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('User Account'),
        null=False,  # Explicitly disallow null
        blank=False  # Explicitly disallow blank
    )

    slug = models.SlugField(
        unique=True,
        verbose_name=_('Account ID'),
        blank=True,  # Allow blank for initial save
        editable=False  # Make it non-editable in admin/forms
    )

    profile_picture = ProcessedImageField(
        default=None,
        upload_to='profile_pics/%Y/%m/%d/',
        processors=[ResizeToFill(150, 150)],
        format='JPEG',
        options={'quality': 100},
        blank=True,
        null=True
    )

    telephone = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name=_('Phone Number'),
        help_text=_('Include country code (e.g. +251 - -- -- -- --)'), 
        region='ET'  # Default region for Ethiopia
    )

    email = models.EmailField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_('Contact Email'),
        help_text=_('Preferred email for communications')
    )

    first_name = models.CharField(
        max_length=30,
        blank=False,  # Changed to match validation
        verbose_name=_('First Name')
    )

    last_name = models.CharField(
        max_length=30,
        blank=False,  # Changed to match validation
        verbose_name=_('Last Name')
    )

    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.INACTIVE,
        verbose_name=_('Account Status')
    )

    role = models.CharField(
        max_length=2,
        choices=Role.choices,
        blank=True,
        null=True,
        verbose_name=_('System Role')
    )

    class Meta:
        ordering = ['-status', 'first_name', 'last_name']
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['role']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def get_absolute_url(self):
        return reverse('profile_detail', kwargs={'slug': self.slug})

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def generate_slug(self):
        """Generate a unique slug using name/email with UUID fallback"""
        base_slug = slugify(f"{self.first_name}-{self.last_name}-{self.email or self.user.email}")
        if not base_slug:
            base_slug = str(uuid.uuid4())[:8]
        return f"{base_slug}-{str(uuid.uuid4())[:4]}"

    def clean(self):
        """Validate model before saving"""
        if not self.email and not self.telephone:
            raise ValidationError(_('Either email or phone number must be provided.'))
        
        # Ensure slug will be unique
        if not self.slug:
            self.slug = self.generate_slug()
        elif Profile.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            raise ValidationError(_('This account ID is already in use.'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
        
        # Skip validation during initial creation (handled in form)
        if not self.pk:
            super().save(*args, **kwargs)
        else:
            self.full_clean()
            super().save(*args, **kwargs)



class Vendor(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_('Vendor Name'),
        unique=True
    )
    slug = models.SlugField(
        unique=True,
        editable=True,
        help_text=_('URL-friendly version of the name'),
        blank=True,  # Allow blank initially
        null=False,  # Don't allow null
        default='',  # Default empty string to avoid migration issues
    )
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name=_('Contact Number')
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Business Address')
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Website URL')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active Vendor')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vendor_detail', kwargs={'slug': self.slug})

    def clean(self):
        if not self.phone_number and not self.website:
            raise ValidationError(_('Provide either a phone number or a website.'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  
        super(Vendor, self).save(*args, **kwargs)  



class Customer(models.Model):
    first_name = models.CharField(
        max_length=100,
        verbose_name=_('First Name')
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Last Name')
    )
    address = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('Full Address'),
        help_text=_('Structured address data')
    )
    email = models.EmailField(
        max_length=254,
        blank=True,
        null=True,
        verbose_name=_('Email Address'),
        unique=True
    )
    phone = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name=_('Phone Number')
    )
    loyalty_points = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Reward Points')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        constraints = [
            models.UniqueConstraint(
                fields=['first_name', 'last_name', 'email'],
                name='unique_customer'
            )
        ]

        # constraints: The constraints list is used to define custom database-level constraints. 
        # In this case, it ensures that the combination of first_name, last_name, and email 
        # is unique across the Customer model, meaning no two customers can have the same 
        # combination of these three fields. This is done using models.UniqueConstraint.

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse('customer_detail', kwargs={'pk': self.pk})

    def get_full_name(self):
        names = [n for n in (self.first_name, self.last_name) if n]
        return ' '.join(names)

    def to_select2(self):
        return {
            "id": self.pk,
            "text": self.get_full_name(),
            "email": self.email or "",
            "phone": str(self.phone) if self.phone else ""
        }
    
    # The to_select2 method is designed to format the customer data in a way that 
    # can be used in a Select2 dropdown (a popular JavaScript library for dynamic dropdowns). 
    # Select2 typically needs a specific structure to function properly, and 
    # this method provides that structure.

    @property
    def is_premium(self):
        return self.loyalty_points > 1000

    def clean(self):
        # Ensure that either an email or phone number is provided
        if not self.email and not self.phone:
            raise ValidationError(_('Customer must have either an email or phone number.'))
