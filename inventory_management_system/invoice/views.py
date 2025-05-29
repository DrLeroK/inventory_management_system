from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django_tables2 import SingleTableView
from django_tables2.export.views import ExportMixin

from .models import Invoice
from .tables import InvoiceTable


class InvoiceBaseView(LoginRequiredMixin):
    """Base view for invoice operations with common settings"""
    model = Invoice
    success_url = reverse_lazy('invoice:invoice-list')


class InvoiceFormMixin:
    """Shared form configuration for create/update views"""
    template_name = 'invoice/invoice_form.html'  # Consider using a single form template
    fields = [
        'customer_name', 
        'contact_number', 
        'item',
        'price_per_item', 
        'quantity', 
        'shipping'
    ]


class InvoiceCreateView(InvoiceFormMixin, InvoiceBaseView, CreateView):
    """Create new invoices"""
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Invoice <strong>{self.object}</strong> was created successfully",
            extra_tags='alert-success'
        )
        return response


class InvoiceUpdateView(InvoiceFormMixin, InvoiceBaseView, UserPassesTestMixin, UpdateView):
    """Update existing invoices (superusers and admins only)"""
    
    def test_func(self):
        """Allow superusers and admins to update"""
        user = self.request.user
        return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'AD')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Invoice <strong>{self.object}</strong> was updated successfully",
            extra_tags='alert-success'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Update {self.object}"
        context['is_updating'] = True
        return context


class InvoiceDeleteView(InvoiceBaseView, UserPassesTestMixin, DeleteView):
    """Delete invoices (superusers and admins only)"""
    template_name = 'invoice/invoice_confirm_delete.html'
    
    def test_func(self):
        """Restrict to superusers and admins"""
        user = self.request.user
        return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'AD')
    
    def form_valid(self, form):
        """Handle successful deletion"""
        invoice = self.get_object()
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Invoice <strong>{invoice}</strong> was deleted successfully",
            extra_tags='alert-danger'
        )
        return response


class InvoiceDetailView(InvoiceBaseView, DetailView):
    """Display invoice details"""
    template_name = 'invoice/invoice_detail.html'
    context_object_name = 'invoice'


class InvoiceListView(ExportMixin, InvoiceBaseView, SingleTableView):
    """List and export invoices with pagination"""
    table_class = InvoiceTable
    template_name = 'invoice/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 25
    table_pagination = False