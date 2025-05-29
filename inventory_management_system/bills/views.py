from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from django_tables2 import SingleTableView
from django_tables2.export.views import ExportMixin

from .models import Bill     
from .tables import BillTable
from accounts.models import Profile


# Created BillBaseView for common settings
class BillBaseView(LoginRequiredMixin):
    """Base view for bill operations with common settings."""
    model = Bill
    success_url = reverse_lazy('bills:bill-list')


# Created BillFormMixin for shared form configuration
class BillFormMixin:
    """Shared form configuration for create/update views."""
    fields = [
        'institution_name',
        'phone_number',
        'email',
        'address',
        'description',
        'payment_details',
        'amount',
        'status'
    ]
    template_name = 'bills/bill_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = hasattr(self, 'object') and self.object is not None and self.object.pk is not None
        return context


class BillCreateView(BillFormMixin, BillBaseView, CreateView):
    """Create new bills."""
    

class BillUpdateView(BillFormMixin, BillBaseView, UserPassesTestMixin, UpdateView):
    """Update existing bills."""
    
    def test_func(self):
        """Restrict to superusers and admins."""
        user = self.request.user
        return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'AD')
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Bill <strong>{self.object}</strong> was updated successfully",
            extra_tags='alert-success'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Update {self.object}"
        context['is_updating'] = True
        return context


class BillDeleteView(BillBaseView, UserPassesTestMixin, DeleteView):
    """Delete bills (superusers and admins only)."""
    template_name = 'bills/bill_confirm_delete.html'
    
    def test_func(self):
        """Restrict to superusers and admins."""
        user = self.request.user
        return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'AD')
    
    def delete(self, request, *args, **kwargs):
        """Handle successful deletion."""
        bill = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f"Bill <strong>{bill}</strong> was deleted successfully",
            extra_tags='alert-danger'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete {self.object}"
        return context
    

class BillListView(ExportMixin, BillBaseView, SingleTableView):
    """List and export bills with pagination."""
    table_class = BillTable
    template_name = 'bills/bill_list.html'
    context_object_name = 'bills'
    paginate_by = 1
    table_pagination = False

# class BillListView(ExportMixin, SingleTableView):
#     """List and export bills with pagination."""
#     model = Bill
#     table_class = BillTable
#     template_name = 'bills/bill_list2.html'
#     context_object_name = 'bills'
#     paginate_by = 25
#     # table_pagination = True

#     export_name = 'bills_export'  # Optional: filename prefix
#     export_formats = ['csv', 'xls', 'xlsx', 'tsv']  # Add/remove formats as needed