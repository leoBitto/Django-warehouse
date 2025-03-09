from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from warehouse.models.base import ProductCategory, Product, ProductAlias, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_primary', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "Nessuna anteprima disponibile"
    image_preview.short_description = _("Anteprima")

class ProductAliasInline(admin.TabularInline):
    model = ProductAlias
    extra = 1
    fields = ('supplier', 'alias_name', 'external_code')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'internal_code', 'category', 'stock_quantity', 'is_visible')
    list_filter = ('category', 'is_visible')
    search_fields = ('name', 'internal_code', 'description')
    readonly_fields = ('internal_code', 'created_at', 'updated_at', 'average_purchase_price', 'average_sales_price', 'gross_margin')
    fieldsets = (
        (_('Informazioni base'), {
            'fields': ('name', 'internal_code', 'category', 'description')
        }),
        (_('Magazzino'), {
            'fields': ('stock_quantity',)
        }),
        (_('Dettagli'), {
            'fields': ('notes', 'is_visible')
        }),
        (_('Informazioni finanziarie'), {
            'fields': ('average_purchase_price', 'average_sales_price', 'gross_margin'),
            'classes': ('collapse',)
        }),
        (_('Metadati'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [ProductImageInline, ProductAliasInline]

    def get_queryset(self, request):
        # Ottimizzazione delle query con prefetch/select_related
        qs = super().get_queryset(request)
        return qs.select_related('category')

    def average_purchase_price(self, obj):
        return f"€ {obj.average_purchase_price:.2f}"
    average_purchase_price.short_description = _("Prezzo medio acquisto")

    def average_sales_price(self, obj):
        return f"€ {obj.average_sales_price:.2f}" 
    average_sales_price.short_description = _("Prezzo medio vendita")

    def gross_margin(self, obj):
        margin = obj.gross_margin
        return f"€ {margin:.2f}" 
    gross_margin.short_description = _("Margine lordo")

@admin.register(ProductAlias)
class ProductAliasAdmin(admin.ModelAdmin):
    list_display = ('product', 'supplier', 'alias_name', 'external_code')
    list_filter = ('supplier',)
    search_fields = ('product__name', 'alias_name', 'external_code', 'supplier__name')
    autocomplete_fields = ['product', 'supplier']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name',)
    readonly_fields = ('image_preview',)
    autocomplete_fields = ['product']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "Nessuna anteprima disponibile"
    image_preview.short_description = _("Anteprima")