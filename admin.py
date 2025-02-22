from django.contrib import admin
from .models.base import ProductCategory, Product, ProductSupplierCode, ProductImage

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
    search_fields = ('name',)
    list_filter = ('parent',)

class ProductSupplierCodeInline(admin.TabularInline):
    model = ProductSupplierCode
    extra = 1
    autocomplete_fields = ['supplier']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'internal_code', 'category', 'stock_quantity', 'is_visible')
    list_filter = ('category', 'is_visible')
    search_fields = ('name', 'internal_code')
    inlines = [ProductSupplierCodeInline, ProductImageInline]
    autocomplete_fields = ['category']
    readonly_fields = ('internal_code',)

class ProductSupplierCodeAdmin(admin.ModelAdmin):
    list_display = ('product', 'supplier', 'external_code', 'description')
    search_fields = ('external_code', 'product__name', 'supplier__name')
    list_filter = ('supplier',)
    autocomplete_fields = ['product', 'supplier']

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'created_at')
    search_fields = ('product__name',)
    list_filter = ('is_primary',)
    autocomplete_fields = ['product']

admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductSupplierCode, ProductSupplierCodeAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
