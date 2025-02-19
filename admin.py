# from django.contrib import admin
# from .models.base import ProductCategory, Product, Sale, Order
# from django.db import transaction

# @admin.register(ProductCategory)
# class ProductCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'parent')
#     search_fields = ('name',)
#     list_filter = ('parent',)
#     ordering = ('name',)

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name',
#                     'internal_code', 
#                     'category', 
#                     'stock_quantity', 
#                     'average_purchase_price', 
#                     'average_sales_price',
#                     'average_profit',
#                     'is_visible')
#     search_fields = ('name', 'internal_code', 'category__name')
#     list_filter = ('category', 'is_visible')
#     ordering = ('name',)
#     readonly_fields = ('internal_code', 'average_purchase_price', 'average_sales_price', 'average_profit')
#     fields = ('name', 'internal_code', 'category', 'stock_quantity', 'is_visible', 'description')

#     def save_model(self, request, obj, form, change):
#         # Assicurarsi che il codice interno venga generato solo quando si crea un nuovo prodotto
#         if not obj.internal_code:
#             obj.internal_code = obj.generate_internal_code()
#         super().save_model(request, obj, form, change)

# @admin.register(Sale)
# class SaleAdmin(admin.ModelAdmin):
#     list_display = ('product', 'customer', 'sale_date', 'delivery_date', 'payment_date', 'quantity', 'unit_price', 'status')
#     search_fields = ('product__name', 'customer__name')
#     list_filter = ('status', 'sale_date', 'delivery_date', 'payment_date')
#     ordering = ('-sale_date',)
#     fields = ('product', 'customer', 'sale_date', 'delivery_date', 'payment_date', 'quantity', 'unit_price', 'status')

#     def save_model(self, request, obj, form, change):
#         # Esegui l'aggiornamento dello stock quando salvi una vendita
#         with transaction.atomic():
#             obj.save()

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('product', 'supplier', 'sale_date', 'delivery_date', 'payment_date', 'quantity', 'unit_price', 'status')
#     search_fields = ('product__name', 'supplier__name')
#     list_filter = ('status', 'sale_date', 'delivery_date', 'payment_date')
#     ordering = ('-sale_date',)
#     fields = ('product', 'supplier', 'sale_date', 'delivery_date', 'payment_date', 'quantity', 'unit_price', 'status')

#     def save_model(self, request, obj, form, change):
#         # Esegui l'aggiornamento dello stock quando salvi un ordine
#         with transaction.atomic():
#             obj.save()
