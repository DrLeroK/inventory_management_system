from django.contrib import admin
from .models import Sale, SaleDetail, Purchase


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer', 'date_added',
        'grand_total', 'amount_paid', 'amount_change'
    )
    search_fields = ('customer__name', 'id')
    list_filter = ('date_added', 'customer')
    ordering = ('-date_added',)
    readonly_fields = ('date_added',)
    date_hierarchy = 'date_added'


@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'sale', 'item',
        'price', 'quantity', 'total_detail'
    )
    search_fields = ('sale__id', 'item__name')
    list_filter = ('sale', 'item')
    ordering = ('sale', 'item')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'slug', 'item', 'vendor',
        'order_date', 'delivery_date',
        'quantity', 'unit_price', 'total_cost', 'status'
    )
    search_fields = ('item__name', 'vendor__name', 'slug')
    list_filter = ('order_date', 'vendor', 'status')
    ordering = ('-order_date',)
    readonly_fields = ('total_cost',)
