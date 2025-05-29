"""
Module: forms.py

Contains Django forms for interacting with inventory and delivery models.

Forms:
- ItemForm: Handles creation and update of inventory items.
- CategoryForm: Handles category creation.
- DeliveryForm: Handles delivery information entry and updates.
"""

from django import forms
from .models import Item, Category, Delivery


class ItemForm(forms.ModelForm):
    """
    Form for creating or updating an Item in the inventory.
    """
    class Meta:
        model = Item
        fields = [
            'name', 'description', 'image', 'category', 'quantity',
            'price', 'expiring_date', 'vendor'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter item name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter item description'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01'
            }),
            'expiring_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
        }


class CategoryForm(forms.ModelForm):
    """
    Form for creating or updating a Category.
    """
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
                'aria-label': 'Category Name'
            }),
        }
        labels = {
            'name': 'Category Name',
        }


class DeliveryForm(forms.ModelForm):
    """
    Form for scheduling or updating a Delivery.
    """
    class Meta:
        model = Delivery
        fields = [
            'item', 'customer_name', 'phone_number',
            'location', 'date', 'is_delivered'
        ]
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-control'
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter delivery location'
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'placeholder': 'Select delivery date and time'
            }),
            'is_delivered': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
