from django.views.generic import ListView
from django.shortcuts import render
from warehouse.models.base import Product, ProductImage

class VisibleProductsListView(ListView):
    model = Product
    template_name = 'products/product_list.html'  # Sostituisci con il percorso del tuo template
    context_object_name = 'products'
    
    def get_queryset(self):
        # Filtriamo solo i prodotti visibili e li preleviamo con le loro immagini (prefetch_related)
        return Product.objects.filter(is_visible=True).prefetch_related('images')