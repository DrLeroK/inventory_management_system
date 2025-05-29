# Django core imports
from django.urls import path

# Local app imports
from .views import (
    BillListView, BillCreateView, 
    BillUpdateView, BillDeleteView
)


app_name = 'bills'

# URL patterns

urlpatterns = [
    # Bill URLs
    path('bills/', BillListView.as_view(), name='bill-list'),
    path('new-bill/', BillCreateView.as_view(), name='bill-create'),
    path('bill/<slug:slug>/update/', BillUpdateView.as_view(), name='bill-update'),
    path('bill/<int:pk>/delete/', BillDeleteView.as_view(), name='bill-delete'),
]
