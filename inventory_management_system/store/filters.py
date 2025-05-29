import django_filters
from django import forms
from .models import Item, Category, Vendor

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Search by name...'})
    )
    
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    vendor = django_filters.ModelChoiceFilter(
        queryset=Vendor.objects.all(),
        empty_label="All Vendors",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    price_min = django_filters.NumberFilter(
        field_name='selling_price', 
        lookup_expr='gte',
        label='Min Price',
        widget=forms.NumberInput(attrs={'placeholder': 'Min'})
    )
    
    price_max = django_filters.NumberFilter(
        field_name='selling_price', 
        lookup_expr='lte',
        label='Max Price',
        widget=forms.NumberInput(attrs={'placeholder': 'Max'})
    )

    class Meta:
        model = Item
        fields = ['name', 'category', 'vendor']
        order_by = [
            ('name', 'Name (A-Z)'),
            ('-name', 'Name (Z-A)'),
            ('selling_price', 'Price (Low-High)'),
            ('-selling_price', 'Price (High-Low)'),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['category'].queryset = Category.objects.order_by('name')
        self.filters['vendor'].queryset = Vendor.objects.order_by('name')