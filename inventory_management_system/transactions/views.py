# Standard library imports
import logging
from decimal import Decimal

# Django core imports
from django.http import JsonResponse, HttpResponse
from django.urls import reverse, reverse_lazy
from django.db import transaction
from django.utils.timezone import localtime

# Class-based views
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Authentication and permissions
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Messaging framework
from django.contrib import messages

# Third-party packages
from openpyxl import Workbook

# Local app imports
from store.models import Item
from accounts.models import Customer
from .models import Sale, Purchase, SaleDetail
from .forms import PurchaseForm, SaleForm


# Create your views here.


logger = logging.getLogger(__name__)


####################################################################################

####################################################################################

def export_sales_to_excel(request):
    """Export sales data to Excel with improved error handling and performance"""
    try:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Sales Report'
        
        # Define headers and column widths
        headers = [
            ('ID', 8),
            ('Date', 20),
            ('Customer', 25),
            ('Sub Total', 15),
            ('Grand Total', 15),
            ('Tax Amount', 15),
            ('Tax Percentage', 15),
            ('Amount Paid', 15),
            ('Amount Change', 15)
        ]
        
        # Write headers and set column widths
        worksheet.append([header[0] for header in headers])
        for col_num, (_, width) in enumerate(headers, 1):
            worksheet.column_dimensions[chr(64 + col_num)].width = width
        
        # Fetch data - FIXED QUERY
        sales = Sale.objects.select_related('customer').all()
        
        for sale in sales:
            worksheet.append([
                sale.id,
                localtime(sale.date_added).replace(tzinfo=None),
                str(sale.customer),  # This will use customer's __str__ method
                sale.sub_total,
                sale.grand_total,
                sale.tax_amount,
                sale.tax_percentage,
                sale.amount_paid,
                sale.amount_change
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="sales_report.xlsx"'},
        )
        workbook.save(response)
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate sales export: {str(e)}", exc_info=True)
        return HttpResponse("Error generating report. Please try again later.", status=500)


def export_purchases_to_excel(request):
    """Export purchase data to Excel with improved structure"""
    try:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Purchases Report'
        
        headers = [
            ('ID', 8),
            ('Item', 25),
            ('Vendor', 25),
            ('Order Date', 20),
            ('Delivery Date', 20),
            ('Quantity', 10),
            ('Status', 15),
            ('Unit Price', 15),
            ('Total Value', 15)
        ]
        
        worksheet.append([header[0] for header in headers])
        for col_num, (_, width) in enumerate(headers, 1):
            worksheet.column_dimensions[chr(64 + col_num)].width = width
        
        purchases = Purchase.objects.select_related('item', 'vendor').only(
            'id', 'item__name', 'vendor__name',
            'order_date', 'delivery_date', 'quantity',
            'status', 'unit_price', 'total_cost'
        )
        
        for purchase in purchases:
            worksheet.append([
                purchase.id,
                purchase.item.name,
                purchase.vendor.name,
                localtime(purchase.order_date).replace(tzinfo=None),
                localtime(purchase.delivery_date).replace(tzinfo=None) if purchase.delivery_date else '',
                purchase.quantity,
                purchase.get_status_display(),
                purchase.unit_price,
                purchase.total_cost
            ])

        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="purchases_report.xlsx"'},
        )
        workbook.save(response)
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate purchases export: {str(e)}", exc_info=True)
        return HttpResponse("Error generating report. Please try again later.", status=500)
    

####################################################################################

####################################################################################

class SaleCreateView(LoginRequiredMixin, CreateView):
    """Handle sale creation with AJAX support."""
    model = Sale
    form_class = SaleForm  # Use the form class for validation
    template_name = "transactions/sale_create.html"


    def get_context_data(self, **kwargs):
        """Add products to the template context"""
        context = super().get_context_data(**kwargs)
        context['products'] = Item.objects.all()  # This makes products available in template
        return context
    
    def post(self, request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return super().post(request, *args, **kwargs)
        
        try:
            # Get and validate customer
            customer_id = request.POST.get('customer')
            if not customer_id:
                return JsonResponse({'error': 'Customer is required'}, status=400)

            # Convert to Decimal safely
            try:
                sub_total = Decimal(request.POST.get('sub_total', '0'))
                tax_percentage = Decimal(request.POST.get('tax_percentage', '0'))
                amount_paid = Decimal(request.POST.get('amount_paid', '0'))
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': 'Invalid numeric input'}, status=400)

            # Get items
            items = []
            i = 0
            while f'items[{i}][id]' in request.POST:
                items.append({
                    'id': request.POST[f'items[{i}][id]'],
                    'price': Decimal(request.POST[f'items[{i}][price]']),
                    'quantity': int(request.POST[f'items[{i}][quantity]'])
                })
                i += 1

            if not items:
                return JsonResponse({'error': 'No items in sale'}, status=400)

            with transaction.atomic():
                # Calculate values FIRST
                tax_amount = sub_total * (tax_percentage / Decimal('100'))
                grand_total = sub_total + tax_amount
                amount_change = amount_paid - grand_total

                # Create sale with ALL values
                sale = Sale.objects.create(
                    customer_id=customer_id,
                    sub_total=sub_total,
                    tax_percentage=tax_percentage,
                    tax_amount=tax_amount,
                    grand_total=grand_total,
                    amount_paid=amount_paid,
                    amount_change=amount_change if amount_change > 0 else Decimal('0')
                )
                
                # Add items
                for item in items:
                    item_obj = Item.objects.get(id=item['id'])
                    SaleDetail.objects.create(
                        sale=sale,
                        item=item_obj,
                        price=item['price'],
                        quantity=item['quantity'],
                        total_detail=item['price'] * item['quantity']
                    )
                    # Update stock
                    item_obj.quantity -= item['quantity']
                    item_obj.save()
                    
            return JsonResponse({'success': True,
                                 'redirect_url': reverse('transactions:sale-list')})
            
        except Exception as e:
            # Only show errors when something actually fails
            return JsonResponse({
                'success': False,
                'error': str(e)  # Show what went wrong
            }, status=400)

   
    def create_sale(self, data):
        """Create and return a new Sale instance."""
        customer = Customer.objects.get(id=int(data['customer']))
        sale = Sale(
            customer=customer,
            sub_total=Decimal(data["sub_total"]),
            tax_percentage=Decimal(data.get("tax_percentage", 0.0)),
            amount_paid=Decimal(data["amount_paid"])
        )
        sale.save()  # Will auto-calculate tax_amount, grand_total, amount_change
        return sale

    
    def create_sale_details(self, sale, items):
        """Create sale details and update inventory."""
        if not isinstance(items, list):
            raise ValueError("Items should be a list")
            
        for item in items:
            if not all(k in item for k in ["id", "price", "quantity", "total_item"]):
                raise ValueError("Item missing required fields")
                
            item_instance = Item.objects.get(id=int(item["id"]))
            if item_instance.quantity < int(item["quantity"]):
                raise ValueError(f"Insufficient stock for {item_instance.name}")
                
            SaleDetail.objects.create(
                sale=sale,
                item=item_instance,
                price=float(item["price"]),
                quantity=int(item["quantity"]),
                total_detail=float(item["total_item"])
            )
            
            # Update inventory
            item_instance.quantity -= int(item["quantity"])
            item_instance.save()


class SaleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a sale (superusers and admins only)."""
    model = Sale
    template_name = "transactions/sale_delete.html"
    context_object_name = "sale"
    pk_url_kwarg = "pk"  # Explicitly tell Django to use 'pk' from the URL
    
    def get_success_url(self):
        return reverse("transactions:sale-list")
    
    def test_func(self):
        """Allow superusers and admins to delete sales"""
        user = self.request.user
        return (
            user.is_superuser or
            (hasattr(user, 'profile') and user.profile.role == 'AD')
        )
    
    
    def form_valid(self, form):
        """Handle successful deletion with rich message"""
        sale = self.get_object()
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Sale record #{sale.id} for <strong>{sale.customer}</strong> was deleted successfully!",
            extra_tags='alert-danger'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete Sale #{self.object.id}"
        context['warning_message'] = "This action cannot be undone!"
        return context
    

class SaleListView(LoginRequiredMixin, ListView):
    """Display paginated list of sales, newest first."""
    model = Sale
    template_name = "transactions/sale_list.html"
    context_object_name = "sales"
    paginate_by = 10
    ordering = ['-date_added']  # Changed to newest first (more common for sales)
    
    def get_queryset(self):
        """Optionally add filtering here if needed later."""
        return super().get_queryset()


class SaleDetailView(LoginRequiredMixin, DetailView):
    """Display detailed view of a single sale."""
    model = Sale
    template_name = "transactions/sale_detail.html"  # Fixed typo in template name
    context_object_name = "sale"  # Explicit is better than implicit


########################################################################

########################################################################

# Created PurchaseCreateUpdateMixin to eliminate duplicate code between create/update views
# Shared template, form, and success URL logic
class PurchaseCreateUpdateMixin:
    """Shared functionality for create and update views"""
    model = Purchase
    form_class = PurchaseForm
    template_name = "transactions/purchase_form.html"  # Singular naming
    context_object_name = "purchase"  # Explicit context name

    def get_success_url(self):
        return reverse("transactions:purchase-list")


class PurchaseCreateView(LoginRequiredMixin, PurchaseCreateUpdateMixin, CreateView):
    """Create new purchase records"""
    # All shared functionality comes from the mixin


class PurchaseUpdateView(LoginRequiredMixin, UserPassesTestMixin, PurchaseCreateUpdateMixin, UpdateView):
    """Update existing purchase records (superusers and admins)"""
    
    def test_func(self):
        """Allow superusers and admins to update purchases"""
        user = self.request.user
        return (
            user.is_superuser or
            (hasattr(user, 'profile') and user.profile.role == 'AD')
        )
    
    def form_valid(self, form):
        """Handle successful update with rich message"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Purchase record #{self.object.id} was updated successfully!",
            extra_tags='alert-success'
        )
        return response

class PurchaseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete purchase records (superusers and admins)"""
    model = Purchase
    template_name = "transactions/purchase_confirm_delete.html"
    context_object_name = "purchase"
    success_url = reverse_lazy("transactions:purchase-list")

    def test_func(self):
        """Allow superusers and admins to delete purchases"""
        user = self.request.user
        return (
            user.is_superuser or
            (hasattr(user, 'profile') and user.profile.role == 'AD')
        )
    
    def form_valid(self, form):
        """Handle successful deletion with rich message"""
        purchase = self.get_object()
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Purchase record #{purchase.id} was deleted successfully!",
            extra_tags='alert-danger'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete Purchase #{self.object.id}"
        context['warning_message'] = "This action cannot be undone!"
        return context

class PurchaseListView(LoginRequiredMixin, ListView):
    """List all purchases with pagination."""
    model = Purchase
    template_name = "transactions/purchase_list.html"  # Singular for consistency
    context_object_name = "purchases"
    paginate_by = 10
    ordering = ['-order_date']  # Added ordering (newest first by default)

    # If you need custom filtering:
    def get_queryset(self):
        return Purchase.objects.select_related('item', 'vendor').all()


class PurchaseDetailView(LoginRequiredMixin, DetailView):
    """Display purchase details."""
    model = Purchase
    template_name = "transactions/purchase_detail.html"  # Consistent naming
    context_object_name = "purchase"  # Explicit context name




