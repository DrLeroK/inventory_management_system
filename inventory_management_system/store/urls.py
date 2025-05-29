# Django core imports
from django.urls import path

# Local app imports
from . import views
from .views import (
    ProductListView, ProductDetailView, ProductCreateView,
    ProductUpdateView, ProductDeleteView, ItemSearchListView, 
    DeliveryListView, DeliveryCreateView, DeliveryUpdateView, 
    DeliveryDeleteView, CategoryListView, CategoryCreateView, 
    CategoryUpdateView, CategoryDeleteView, DashboardView,
)


app_name = 'store'

# URL patterns

urlpatterns = [
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),

    # Product URLs
    path('products/', ProductListView.as_view(), name='product-list'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('new-product/', ProductCreateView.as_view(), name='product-create'),
    path('product/<slug:slug>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('product/<slug:slug>/delete/', ProductDeleteView.as_view(), name='product-delete'),

    # Item search
    path('search/', ItemSearchListView.as_view(), name='item_search_list_view'),

    # Delivery URLs
    path('deliveries/', DeliveryListView.as_view(), name='deliveries'),
    path('new-delivery/', DeliveryCreateView.as_view(),name='delivery-create'),
    path('delivery/<int:pk>/update/', DeliveryUpdateView.as_view(), name='delivery-update'),
    path('delivery/<int:pk>/delete/', DeliveryDeleteView.as_view(),name='delivery-delete'),

    # AJAX view
    path('get-items/', views.get_items_ajax_view, name='get_items'),

    # Category URLs
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
]
