from django.contrib import admin
from .models import Supplier, Item, Allergen, Ingredient, Purchase

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'address')
    search_fields = ('name', 'contact', 'address')

@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ('pdv',)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('item', 'supplier', 'unit_price', 'quantity', 'purchase_date', 'payment_date')
    list_filter = ('supplier', 'purchase_date', 'payment_date')
