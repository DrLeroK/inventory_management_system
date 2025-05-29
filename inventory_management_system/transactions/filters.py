import django_filters
from django import forms
from myDjangoEnv.basic_form.first_form_app import models
from .models import Sale, Purchase
from store.models import Item
from accounts.models import Vendor 


class SaleFilter(django_filters.FilterSet):
    transaction_date = django_filters.DateFromToRangeFilter(
        field_name='transaction_date',
        label='Date Range',
        widget=django_filters.widgets.RangeWidget(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    class Meta:
        model = Sale
        fields = {
            'item': ['exact'],
            'profile': ['exact'],
            'transaction_date': ['exact', 'lt', 'gt']
        }
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': django_filters.DateTimeFilter,
                'extra': lambda f: {
                    'widget': forms.DateInput(
                        attrs={'type': 'date', 'class': 'form-control'}
                    )
                }
            }
        }


class PurchaseFilter(django_filters.FilterSet):
    item = django_filters.ModelChoiceFilter(
        queryset=None,  # Will be set in __init__
        label='Product',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    vendor = django_filters.ModelChoiceFilter(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    delivery_status = django_filters.ChoiceFilter(
        choices=Purchase.DELIVERY_STATUS,
        empty_label="All Statuses",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Purchase
        fields = ['item', 'vendor', 'delivery_status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['item'].queryset = Item.objects.all().order_by('name')
        self.filters['vendor'].queryset = Vendor.objects.all().order_by('name')