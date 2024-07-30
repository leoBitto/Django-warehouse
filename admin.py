from django.contrib import admin
from .models import Category, Product, Sale, Order

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('type',)
    search_fields = ('type',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category')
    search_fields = ('name', 'code')
    list_filter = ('category',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'sale_date', 'delivery_date', 'quantity', 'unit_price', 'customer')
    search_fields = ('product__name', 'customer__name')
    list_filter = ('sale_date', 'customer')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'sale_date', 'delivery_date', 'quantity', 'unit_price', 'supplier')
    search_fields = ('product__name', 'supplier__name')
    list_filter = ('sale_date', 'supplier')
