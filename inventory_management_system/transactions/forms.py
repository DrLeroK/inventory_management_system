from django import forms
from django.forms import ModelForm
from decimal import Decimal
from .models import Sale, SaleDetail, Purchase


class SaleForm(ModelForm):
    """
    Enhanced form with:
    - Automatic calculations
    - Crispy forms integration
    - Better field validation
    """
    class Meta:
        model = Sale
        fields = ['customer', 'sub_total', 'tax_percentage', 'amount_paid']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select customer...'
            }),
            'sub_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'readonly': 'readonly'  # Typically calculated from items
            }),
            'tax_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_total'].initial = Decimal('0.00')
        self.fields['tax_percentage'].initial = Decimal('0.00')
        self.fields['amount_paid'].initial = Decimal('0.00')

    def clean(self):
        cleaned_data = super().clean()
        amount_paid = cleaned_data.get('amount_paid')
        sub_total = cleaned_data.get('sub_total')
        tax_percentage = cleaned_data.get('tax_percentage')

        if amount_paid is not None and amount_paid < Decimal('0.00'):
            raise forms.ValidationError("Amount paid cannot be negative")

        if sub_total is not None and sub_total < Decimal('0.00'):
            raise forms.ValidationError("Subtotal cannot be negative")

        if tax_percentage is not None and tax_percentage < Decimal('0.00'):
            raise forms.ValidationError("Tax percentage cannot be negative")

        return cleaned_data


#################################################################################
class SaleDetailForm(forms.ModelForm):
    """
    Form for individual line items in a sale (SaleDetail).
    total_detail is auto-calculated and not included in the form.
    """
    class Meta:
        model = SaleDetail
        fields = ['item', 'price', 'quantity']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


#################################################################################
class PurchaseForm(forms.ModelForm):
    """
    Form for creating or updating an inventory purchase.
    total_cost is auto-calculated in the model's save() method.
    """
    class Meta:
        model = Purchase
        fields = ['item', 'vendor', 'quantity', 'unit_price', 'status', 'notes']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
