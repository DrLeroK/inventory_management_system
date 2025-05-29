# Django core imports
from django.urls import path

# Local app imports
from .views import (
    PurchaseListView, PurchaseDetailView, PurchaseCreateView,
    PurchaseUpdateView, PurchaseDeleteView, SaleListView,
    SaleDetailView, SaleCreateView, SaleDeleteView,
    export_sales_to_excel, export_purchases_to_excel
)

app_name = 'transactions'


# URL patterns
urlpatterns = [
    # Purchase URLs
    path('purchases/', PurchaseListView.as_view(), name='purchase-list'),
    path('purchase/<slug:slug>/', PurchaseDetailView.as_view(), name='purchase-detail'),
    path('new-purchase/', PurchaseCreateView.as_view(), name='purchase-create'),
    path('purchase/<int:pk>/update/', PurchaseUpdateView.as_view(), name='purchase-update'),
    path('purchase/<int:pk>/delete/', PurchaseDeleteView.as_view(), name='purchase-delete'),

    # Sale URLs
    path('sales/', SaleListView.as_view(), name='sale-list'),
    path('sale/<int:pk>/', SaleDetailView.as_view(), name='sale-detail'),
    path('new-sale/', SaleCreateView.as_view(), name='sale-create'),
    path('sale/<int:pk>/delete/', SaleDeleteView.as_view(), name='sale-delete'),

    # Sales and purchases export
    path('sales/export/', export_sales_to_excel, name='sale-export'),
    path('purchases/export/', export_purchases_to_excel, name='purchase-export'),
]