from django.urls import path
from .views import LoginView, LogoutView


# Local app imports
from .views import (
    ProfileListView,
    ProfileCreateView,
    ProfileUpdateView, 
    ProfileDeleteView,
    CustomerListView,
    CustomerCreateView,
    CustomerUpdateView,
    CustomerDeleteView,
    get_customers,
    VendorListView,
    VendorCreateView,
    VendorUpdateView,
    VendorDeleteView,
    ProfileView,
)


app_name = 'accounts'


urlpatterns = [
    # User authentication URLs
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # Profile URLs
    path('profiles/', ProfileListView.as_view(), name='profile-list'),
    path('new-profile/', ProfileCreateView.as_view(), name='profile-create'),
    path('profile/<int:pk>/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/<int:pk>/delete/', ProfileDeleteView.as_view(), name='profile-delete'),

    # Customer URLs
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/create/', CustomerCreateView.as_view(), name='customer-create'),
    path('customers/<int:pk>/update/', CustomerUpdateView.as_view(), name='customer-update'),
    path('customers/<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer-delete'),
    path('get_customers/', get_customers, name='get-customers'),

    # Vendor URLs
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
    path('vendors/new/', VendorCreateView.as_view(), name='vendor-create'),
    path('vendors/<int:pk>/update/', VendorUpdateView.as_view(), name='vendor-update'),
    path('vendors/<int:pk>/delete/', VendorDeleteView.as_view(), name='vendor-delete'),
]
