from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import Profile, Customer, Vendor



###############################################################

class ProfileForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'required': 'required'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'required': 'required'})
    )
    telephone = forms.CharField(
        max_length=20,
        required=False,
        help_text="Include country code (e.g. +1 555 123 4567)"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'required': 'required'})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    status = forms.ChoiceField(
        choices=Profile.Status.choices,
        initial=Profile.Status.INACTIVE
    )
    role = forms.ChoiceField(
        choices=Profile.Role.choices,
        required=False
    )

    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'telephone',
            'profile_picture',
            'status',
            'role',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Create or update profile
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': self.cleaned_data['first_name'],
                    'last_name': self.cleaned_data['last_name'],
                    'email': self.cleaned_data['email'],
                    'status': self.cleaned_data['status'],
                    'role': self.cleaned_data['role'],
                    'telephone': self.cleaned_data.get('telephone', ''),
                }
            )
            
            # Handle profile picture upload
            if self.cleaned_data.get('profile_picture'):
                profile.profile_picture = self.cleaned_data['profile_picture']
            
            if not created:
                # Update existing profile if needed
                profile.first_name = self.cleaned_data['first_name']
                profile.last_name = self.cleaned_data['last_name']
                profile.email = self.cleaned_data['email']
                profile.status = self.cleaned_data['status']
                profile.role = self.cleaned_data['role']
                profile.telephone = self.cleaned_data.get('telephone', '')
            
            profile.save()
        
        return user



class ProfileUpdateForm(UserChangeForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'required': 'required'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'required': 'required'})
    )
    telephone = forms.CharField(
        max_length=20,
        required=False,
        help_text="Include country code (e.g. +251 - -- -- -- --)"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'required': 'required'})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    status = forms.ChoiceField(
        choices=Profile.Status.choices
    )
    role = forms.ChoiceField(
        choices=Profile.Role.choices,
        required=False
    )

    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'telephone',
            'profile_picture',
            'status',
            'role'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password field from UserChangeForm
        self.fields.pop('password', None)
        # Set initial values from profile
        if hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            self.fields['first_name'].initial = profile.first_name
            self.fields['last_name'].initial = profile.last_name
            self.fields['telephone'].initial = profile.telephone
            self.fields['status'].initial = profile.status
            self.fields['role'].initial = profile.role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Get or create profile
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': self.cleaned_data['first_name'],
                    'last_name': self.cleaned_data['last_name'],
                    'email': self.cleaned_data['email'],
                    'status': self.cleaned_data['status'],
                    'role': self.cleaned_data['role'],
                    'telephone': self.cleaned_data.get('telephone', ''),
                }
            )
            
            # Update profile fields
            if not created:
                profile.first_name = self.cleaned_data['first_name']
                profile.last_name = self.cleaned_data['last_name']
                profile.email = self.cleaned_data['email']
                profile.status = self.cleaned_data['status']
                profile.role = self.cleaned_data['role']
                profile.telephone = self.cleaned_data.get('telephone', '')
            
            # Handle profile picture upload
            if self.cleaned_data.get('profile_picture'):
                profile.profile_picture = self.cleaned_data['profile_picture']
            
            profile.save()
        
        return user

######################################################################################    

class CustomerForm(forms.ModelForm):
    """Form for creating/updating customer information."""
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'address', 'email', 'phone', 'loyalty_points']
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'address': _('Address'),
            'email': _('Email Address'),
            'phone': _('Phone Number'),
            'loyalty_points': _('Reward Points'),
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter first name')}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter last name')}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Enter address'), 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter email')}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter phone number')}),
            'loyalty_points': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Enter loyalty points')}),
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        if not email and not phone:
            raise forms.ValidationError(_("Customer must have either an email or phone number."))
        

class CustomerUpdateForm(forms.ModelForm):
    """Form for updating existing customer information."""

    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'address',
            'email',
            'phone',
            'loyalty_points'
        ]
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'address': _('Full Address'),
            'email': _('Email Address'),
            'phone': _('Phone Number'),
            'loyalty_points': _('Loyalty Points'),
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter first name')}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter last name')}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Enter address'), 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter email')}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter phone number')}),
            'loyalty_points': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Enter loyalty points')}),
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        if not email and not phone:
            raise forms.ValidationError(_("Please provide at least an email or a phone number."))

        # Check for duplicate email (excluding the current instance)
        if email:
            qs = Customer.objects.exclude(pk=self.instance.pk).filter(email__iexact=email)
            if qs.exists():
                raise forms.ValidationError(_("A customer with this email already exists."))

        return cleaned_data


##########################################################################################

class VendorForm(forms.ModelForm):
    """Form for creating/updating vendor information."""
    class Meta:
        model = Vendor
        fields = ['name', 'phone_number', 'address']
        labels = {
            'name': _('Vendor Name'),
            'phone_number': _('Contact Number'),
            'address': _('Business Address'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Vendor Name')}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Phone Number')}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Address')}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        if Vendor.objects.exclude(pk=self.instance.pk).filter(name__iexact=name).exists():
            raise forms.ValidationError(_("A vendor with this name already exists."))




class VendorUpdateForm(forms.ModelForm):
    """Form for updating existing vendor information."""

    class Meta:
        model = Vendor
        fields = ['name', 'phone_number', 'address']
        labels = {
            'name': _('Vendor Name'),
            'phone_number': _('Phone Number'),
            'address': _('Business Address'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Vendor Name')}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Phone Number')}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Business Address')}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if Vendor.objects.exclude(pk=self.instance.pk).filter(name__iexact=name).exists():
            raise forms.ValidationError(_("A vendor with this name already exists."))
        return name