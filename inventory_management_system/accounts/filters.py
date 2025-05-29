import django_filters
from django.db import models
from django import forms
from .models import Profile


class StaffFilter(django_filters.FilterSet):
    """Advanced filtering for staff profiles with multiple filter types and customization."""
    
    # Custom field filters
    search = django_filters.CharFilter(
        method='custom_search',
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Name, email, or username...'})
    )
    
    role = django_filters.MultipleChoiceFilter(
        choices=Profile.Role.choices,
        widget=forms.CheckboxSelectMultiple,
        label='Roles'
    )
    
    status = django_filters.MultipleChoiceFilter(
        choices=Profile.Status.choices,
        widget=forms.CheckboxSelectMultiple,
        label='Status'
    )
    
    created_after = django_filters.DateFilter(
        field_name='user__date_joined',
        lookup_expr='gte',
        label='Joined after',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Profile
        fields = {
            'email': ['exact', 'contains'],
            'user__username': ['exact', 'contains'],
            'telephone': ['exact', 'contains'],
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email filter case-insensitive
        self.filters['email'].lookup_expr = 'iexact'
        self.filters['email__contains'].lookup_expr = 'icontains'
        
        # Add custom labels
        self.filters['user__username__contains'].label = 'Username contains'
        self.filters['telephone__contains'].label = 'Phone contains'
    
    def custom_search(self, queryset, name, value):
        """Custom search across multiple fields"""
        return queryset.filter(
            models.Q(first_name__icontains=value) |
            models.Q(last_name__icontains=value) |
            models.Q(email__icontains=value) |
            models.Q(user__username__icontains=value)
        )
    
    @property
    def qs(self):
        """Override to add default ordering"""
        qs = super().qs
        return qs.select_related('user').order_by('last_name', 'first_name')
    
    