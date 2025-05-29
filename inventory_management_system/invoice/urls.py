# Django core imports
from django.urls import path


# Local app imports
from .views import (
    InvoiceListView, InvoiceDetailView,
    InvoiceCreateView, InvoiceUpdateView,
    InvoiceDeleteView, 
)

app_name = 'invoice'


# URL patterns
urlpatterns = [
    # Invoice URLs
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'),
    path('invoice/<slug:slug>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('new-invoice/', InvoiceCreateView.as_view(),name='invoice-create'),
    path('invoice/<slug:slug>/update/', InvoiceUpdateView.as_view(), name='invoice-update'),
    path('invoice/<int:pk>/delete/', InvoiceDeleteView.as_view(), name='invoice-delete'),
]

