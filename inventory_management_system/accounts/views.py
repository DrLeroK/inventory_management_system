# Django core imports

# Used to return JSON data in a view.
from django.http import JsonResponse
from django.urls import reverse_lazy

# Authentication and permissions
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Returns the custom User model you define (if any)
from django.contrib.auth import get_user_model
# Allows you to add success, warning, or error messages
from django.contrib import messages

# Class-based views
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

# Used for rendering HTML tables from Django QuerySets easily.
from django_tables2 import SingleTableView

# Adds CSV/Excel export functionality to your table views
from django_tables2.export.views import ExportMixin

# Local app imports
from .models import Profile, Customer, Vendor
from .forms import (
    ProfileUpdateForm, CustomerForm,
    VendorForm, ProfileForm, 
    CustomerUpdateForm, VendorUpdateForm
)

from .tables import ProfileTable

# Enables complex queries with OR/AND conditions
from django.db.models import Q

# Restricts views to specific HTTP methods (GET, POST, etc.)
from django.views.decorators.http import require_http_methods

# for login and logout
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.views import LogoutView as AuthLogoutView



# CREATE YOUR VIEWS HERE

class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_invalid(self, form):
        messages.error(self.request, "Invalid credentials. Please try again.")
        return super().form_invalid(form)


class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('accounts:login')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

#######################################################

##########################################################
class ProfileCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    # This tells Django the model being created is the User model, not just the Profile.
    model = get_user_model()  # Now creating User, not Profile
    form_class = ProfileForm
    template_name = 'accounts/profile_create.html'
    success_url = reverse_lazy('accounts:profile-list')
    
    def test_func(self):
        # Only allow superusers or admins to update profiles
        user = self.request.user
        return self.request.user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'AD')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Profile created successfully")
        return response
    

class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:profile-list')
    
    def test_func(self):
        # Only allow superusers or admins to update profiles
        user = self.request.user
        return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'AD')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Profile updated successfully")
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_updating'] = True
        return context   


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    login_url = 'accounts:login'  # Redirects to login if user is not authenticated


class ProfileListView(LoginRequiredMixin, ExportMixin, SingleTableView):
    model = Profile  
    table_class = ProfileTable  # Uses your custom table
    template_name = 'accounts/stafflist.html' 
    context_object_name = 'profiles'
    paginate_by = 10  # 10 items per page
    table_pagination = True  # Consider enabling if using tables2 pagination

    login_url = 'accounts:login'  # Optional: redirects unauthenticated users
    raise_exception = False  # Set to True to raise PermissionDenied instead of redirect

    def get_queryset(self):
        # Customize queryset (e.g. show only active staff or filtered by user role)
        return Profile.objects.select_related('user').all()
    
    # Add this to properly handle pagination
    def get_table_pagination(self, table):
        return {'per_page': self.paginate_by}
        

class ProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Profile
    template_name = 'accounts/profile_confirm_delete.html'
    success_url = reverse_lazy('accounts:profile-list')
    
    def test_func(self):
        """
        Allow deletion if:
        1. User is superuser OR admin (role='AD')
        2. Not trying to delete themselves
        3. Not trying to delete another admin (unless superuser)
        """
        profile_to_delete = self.get_object()
        user = self.request.user
        
        # Prevent self-deletion
        if user == profile_to_delete.user:
            return False
        
        # Superusers can delete anyone (except themselves)
        if user.is_superuser:
            return True
        
        # Admins can only delete non-admin, non-superuser profiles
        if hasattr(user, 'profile') and user.profile.role == 'AD':
            target_user = profile_to_delete.user
            return not (target_user.is_superuser or 
                      (hasattr(target_user, 'profile') and target_user.profile.role == 'AD'))
        
        return False
    
    def form_valid(self, form):
        """
        Handle successful form submission (deletion)
        This replaces the delete() method to work with FormMixin
        """
        profile = self.get_object()
        username = profile.user.username
        response = super().form_valid(form)
        messages.success(self.request, f"Successfully deleted profile for {username}")
        return response
    
###############################################################

###############################################################

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'accounts/customer_form.html'
    success_url = reverse_lazy('accounts:customer-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Customer created successfully")
        return super().form_valid(form)


class CustomerUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Customer
    form_class = CustomerUpdateForm
    template_name = 'accounts/customer_form.html'
    success_url = reverse_lazy('accounts:customer_list')
    
    def test_func(self):
        """Only allow superusers and admins to update customers"""
        user = self.request.user
        return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'AD')
    
    def form_valid(self, form):
        """Handle successful form submission"""
        response = super().form_valid(form)
        full_name = form.instance.get_full_name()
        messages.success(
            self.request, 
            f"Customer <strong>{full_name}</strong> was updated successfully",
            extra_tags='alert-success'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Update {self.object.get_full_name()}"
        context['is_updating'] = True
        return context


class CustomerDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Customer
    template_name = 'accounts/customer_confirm_delete.html'
    success_url = reverse_lazy('accounts:customer_list')
    
    def test_func(self):
        """Only allow superusers and admins to delete customers"""
        user = self.request.user
        return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'AD')
    
    def form_valid(self, form):
        """Handle successful deletion"""
        customer = self.get_object()
        full_name = customer.get_full_name()
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Customer <strong>{full_name}</strong> was deleted successfully",
            extra_tags='alert-danger'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['related_objects'] = self.object.orders.all()[:5]  # Show related orders
        # context['related_count'] = self.object.orders.count()  # Show total related orders
        return context


class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'accounts/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if search := self.request.GET.get('search'):
            return queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset
    

@require_http_methods(["GET", "POST"])
@login_required
def get_customers(request):
    term = request.GET.get('term') or request.POST.get('term', '')
    # It prioritizes GET if term is passed as a query parameter.

    if not term:
        return JsonResponse({'results': []})

    customers = Customer.objects.filter(
        Q(first_name__icontains=term) |
        Q(last_name__icontains=term) |
        Q(email__icontains=term))[:20]
    # Uses Q objects to allow OR conditions in the filter:
    # first_name contains term
    # OR last_name contains term
    # OR email contains term
    
    results = [{
        'id': c.id,
        'text': c.get_full_name(),
        'email': c.email,
        'loyalty_points': c.loyalty_points,
        'is_premium': c.is_premium,
    } for c in customers]
    # Prepares the result list in a format suitable for Select2, which expects:
    
#     {
#   "results": [
#     {"id": 1, "text": "John Doe", "email": "john@example.com"},
#     {"id": 2, "text": "Jane Smith", "email": "jane@example.com"}
#        ]
#       }
    return JsonResponse({'results': results})

##############################################################

###############################################################

class VendorCreateView(LoginRequiredMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'accounts/vendor_form.html'
    success_url = reverse_lazy('accounts:vendor-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Vendor created successfully")
        return super().form_valid(form)


class VendorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Vendor
    form_class = VendorUpdateForm
    template_name = 'accounts/vendor_form.html'
    success_url = reverse_lazy('accounts:vendor-list')
    
    def test_func(self):
        """Only allow superusers and admins to update vendors"""
        user = self.request.user
        return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'AD')
    
    def form_valid(self, form):
        """Handle successful form submission"""
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f"Vendor <strong>{form.instance.name}</strong> was updated successfully",
            extra_tags='alert-success'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Update {self.object.name}"
        context['is_updating'] = True
        return context


class VendorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Vendor
    template_name = 'accounts/vendor_confirm_delete.html'
    success_url = reverse_lazy('accounts:vendor-list')
    
    def test_func(self):
        """Only allow superusers and admins to delete vendors"""
        user = self.request.user
        return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'AD')
    
    def delete(self, request, *args, **kwargs):
        """Handle successful deletion"""
        vendor = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(
            self.request,
            f"Vendor <strong>{vendor.name}</strong> was deleted successfully",
            extra_tags='alert-danger'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['related_objects'] = self.object.products.all()[:5]  # Show related products
        # context['related_count'] = self.object.products.count()  # Show total related products
        return context
    

class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    template_name = 'accounts/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 20
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if search := self.request.GET.get('search'):
            return queryset.filter(
                Q(name__icontains=search) |
                Q(contact_person__icontains=search)
            )
        return queryset