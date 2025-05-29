# Standard library imports
import operator
from functools import reduce
from django.views.decorators.http import require_http_methods
from django.core.exceptions import BadRequest

# Django core imports
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta

# Authentication and permissions
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

# Class-based views
from django.views.generic import (
    DetailView, CreateView, 
    UpdateView, DeleteView, 
    ListView, TemplateView,
)

# Third-party packages
from django_tables2 import SingleTableView
import django_tables2 as tables
from django_tables2.export.views import ExportMixin
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied, BadRequest

from django.views.decorators.http import require_http_methods

# Local app imports
from accounts.models import Profile
from transactions.models import Sale
from .models import Category, Item, Delivery
from .forms import ItemForm, CategoryForm, DeliveryForm
from .tables import ItemTable, DeliveryTable

import logging


logger = logging.getLogger(__name__)


# Create your views here.

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "store/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic counts
        context['profiles_count'] = Profile.objects.count()
        context['total_items'] = Item.objects.aggregate(
            total=Sum('quantity')
        )['total'] or 0
        context['delivery_count'] = Delivery.objects.count()
        context['sales_count'] = Sale.objects.count()
        context['items_count'] = Item.objects.count()

        
        # Optimized queries with select_related
        context['recent_items'] = Item.objects.select_related(
            'category', 'vendor'
        ).order_by('-id')[:5]
        
        context['recent_sales'] = Sale.objects.select_related(
            'customer'
        ).order_by('-date_added')[:5]
    
        
        return context
    
    


#######################################################################

########################################################################


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = "store/product_form.html"  # More standard name
    success_url = reverse_lazy('store:product-list')  # URL name instead of hardcoded path

    def form_valid(self, form):
        messages.success(self.request, "Product created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below")
        return super().form_invalid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = "store/product_form.html"
    success_url = reverse_lazy('store:product-list')

    def test_func(self):
        """Allow superusers, admins, and users with change permission"""
        user = self.request.user
        return (
            user.is_superuser or 
            user.has_perm('store.change_item') or
            (hasattr(user, 'profile') and user.profile.role == 'AD')
        )

    def form_valid(self, form):
        """Handle successful form submission"""
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f"Product <strong>{self.object.name}</strong> was updated successfully!",
            extra_tags='alert-success'
        )
        return response

    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Update {self.object.name}"
        return context


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Item
    template_name = "store/product_confirm_delete.html"
    success_url = reverse_lazy('store:product-list')

    def test_func(self):
        """Allow superusers, admins, and users with delete permission"""
        user = self.request.user
        return (
            user.is_superuser or 
            user.has_perm('store.delete_item') or
            (hasattr(user, 'profile') and user.profile.role == 'AD')
        )

    def form_valid(self, form):
        """Handle successful deletion"""
        product = self.get_object()
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Product <strong>{product.name}</strong> was deleted successfully!",
            extra_tags='alert-danger'
        )
        return response

    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete {self.object.name}"
        # context['related_objects'] = self.object.orders.all()[:5]  # Example related objects
        return context
    

class ProductListView(LoginRequiredMixin, ExportMixin, SingleTableView):
    """
    Enhanced product list view with optimized queries and export options
    
    Maintains all original functionality while improving:
    - Query efficiency
    - Export configuration
    - Pagination control
    """
    model = Item
    table_class = ItemTable
    template_name = "store/products_list.html"
    context_object_name = "items"
    paginate_by = 10
    export_name = "products"  # Base filename for exports
    export_trigger_param = "export"  # URL parameter for exports
    context_object_name = "items"
    
    # Optimize database queries
    def get_queryset(self):
        return super().get_queryset().select_related(
            'category', 'vendor'
        ).only(
            'name', 
            'price', 
            'quantity',
            'category__name',
            'vendor__name'
        )
    
    # Control what gets exported
    def get_export_filename(self, export_format):
        return f"{self.export_name}_{timezone.now().date()}.{export_format}"
    
    # ADDED JUST KNOW
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Item.objects.all()  # Or filter as needed
        return context
    

class ItemSearchListView(ProductListView):
    """
    Enhanced item search with:
    - Search across multiple fields (name, category, vendor)
    - More flexible search logic
    - Preserved original filtering capabilities
    """
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        
        if query:
            query_list = query.split()
            # Search across multiple fields with OR between terms
            q_objects = [
                Q(name__icontains=term) | 
                Q(category__name__icontains=term) |
                Q(vendor__name__icontains=term)
                for term in query_list
            ]
            queryset = queryset.filter(reduce(operator.and_, q_objects))
        
        return queryset.distinct()  # Avoid duplicates from multi-field matches


class ProductDetailView(LoginRequiredMixin, DetailView):
    """
    Enhanced product detail view with:
    - Related items display
    - Better context data
    - Optimized queries
    """
    model = Item
    template_name = "store/product_detail.html"
    context_object_name = "item"
    
    def get_success_url(self):
        return reverse("store:product-detail", kwargs={"slug": self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_items'] = Item.objects.filter(
            category=self.object.category
        ).exclude(
            pk=self.object.pk
        ).select_related('vendor')[:4]  # Get 4 related items
        return context

    def get_queryset(self):
        return super().get_queryset().select_related('category', 'vendor')
############################################################################

###########################################################################


class DeliveryCreateView(LoginRequiredMixin, CreateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = "store/delivery_form.html"
    success_url = reverse_lazy('store:deliveries')  # Using URL name
    
    def form_valid(self, form):
        messages.success(self.request, "Delivery created successfully!")
        return super().form_valid(form)


class DeliveryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = "store/delivery_form.html"
    success_url = reverse_lazy('store:deliveries')
    
    def test_func(self):
        """Allow superusers, admins, and users with change permission"""
        user = self.request.user
        return (
            user.is_superuser or
            user.has_perm('store.change_delivery') or
            (hasattr(user, 'profile') and user.profile.role == 'AD')
        )
    
    def form_valid(self, form):
        """Handle successful form submission with rich message"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Delivery <strong>{self.object}</strong> was updated successfully!",
            extra_tags='alert-success'
        )
        return response

class DeliveryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Delivery
    template_name = "store/delivery_confirm_delete.html"
    success_url = reverse_lazy('store:deliveries')
    
    def test_func(self):
        """Allow superusers, admins, and users with delete permission"""
        user = self.request.user
        return (
            user.is_superuser or
            user.has_perm('store.delete_delivery') or
            (hasattr(user, 'profile') and user.profile.role == 'AD')
        )
    
    def form_valid(self, form):
        """Handle successful deletion with rich message"""
        delivery = self.get_object()
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Delivery <strong>{delivery}</strong> was deleted successfully!",
            extra_tags='alert-danger'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete {self.object}"
        return context
    

class DeliveryListView(LoginRequiredMixin, ExportMixin, tables.SingleTableView):
    model = Delivery
    table_class = DeliveryTable  # Add custom table configuration
    template_name = "store/deliveries.html"
    context_object_name = "deliveries"
    paginate_by = 10
    export_name = "deliveries_export"  # Better export filename
    
    def get_queryset(self):
        return super().get_queryset().select_related('item')


class DeliverySearchListView(DeliveryListView):
    search_fields = ['customer_name', 'item__name', 'location']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        
        if query:
            queries = [Q(**{f"{field}__icontains": query}) 
                      for field in self.search_fields]
            queryset = queryset.filter(reduce(operator.or_, queries))
        return queryset.distinct()
    

#########################################################################

###########################################################################

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'store/category_form.html'
    success_url = reverse_lazy('store:category-list')
    
    # def get_success_url(self):
    #     return reverse_lazy('store:category-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, "Category created successfully!")
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'store/category_form.html'
    success_url = reverse_lazy('store:category-list')

    def test_func(self):
        """Allow superusers, admins, and staff to delete categories"""
        user = self.request.user
        return (
            user.is_superuser or 
            user.is_staff or
            (hasattr(user, 'profile') and user.profile.role == 'AD')
        )

    def form_valid(self, form):
        """Handle successful form submission with rich message"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Category <strong>{self.object.name}</strong> was updated successfully!",
            extra_tags='alert-success'
        )
        return response

    # def get_success_url(self):
    #     return reverse_lazy('store:category-detail', kwargs={'pk': self.object.pk})


class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    template_name = 'store/category_confirm_delete.html'
    context_object_name = 'category'
    success_url = reverse_lazy('store:category-list')

    def test_func(self):
        """Allow superusers, admins, and staff to delete categories"""
        user = self.request.user
        return (
            user.is_superuser or 
            user.is_staff or
            (hasattr(user, 'profile') and user.profile.role == 'AD')
        )

    def form_valid(self, form):
        """Handle successful deletion with rich message"""
        category = self.get_object()
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Category <strong>{category.name}</strong> was deleted successfully!",
            extra_tags='alert-danger'
        )
        return response

    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete {self.object.name}"
        context['warning_message'] = "This will also delete all related items!"
        return context


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'store/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    
    def get_queryset(self):
        return super().get_queryset().annotate(
            item_count=Count('item')
        )

    
#########################################################

#########################################################

# To allow AJAX-based searching of items by either GET or POST, based on the term query 
# (used for real-time suggestions or dynamic filtering).
@require_http_methods(["GET", "POST"])
@login_required
def item_search(request):
    """AJAX endpoint for item search with better error handling"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        raise PermissionDenied("AJAX requests only")

    term = request.GET.get('term') or request.POST.get('term', '')
    if not term or len(term) < 2:
        return JsonResponse({'error': 'Search term too short'}, status=400)

    try:
        items = Item.objects.filter(
            Q(name__icontains=term) |
            Q(category__name__icontains=term)
        )[:10]
        data = [item.to_json() for item in items]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': 'Server error'}, status=500)
    


# Another AJAX endpoint, but only accepts POST, and is a bit more controlled
#  (used possibly in a secure JS environment or embedded admin system).
@require_http_methods(["POST"])
@csrf_exempt
@login_required
def get_items_ajax_view(request):
    """
    AJAX endpoint for searching items.
    Returns JSON response of items matching search term.
    """
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        raise BadRequest("This endpoint only accepts AJAX requests")
    
    try:
        search_term = request.POST.get("term", "").strip()
        if not search_term:
            return JsonResponse([], safe=False)
        
        items = Item.objects.filter(
            name__icontains=search_term
        ).select_related('category', 'vendor')[:10]
        
        return JsonResponse(
            [item.to_json() for item in items],
            safe=False
        )
        
    except Exception as e:
        logger.error(f"Error in item search: {str(e)}")
        return JsonResponse(
            {'error': 'An error occurred during search'},
            status=500
        )

