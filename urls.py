from django.urls import path
from warehouse.views.base import *
from warehouse.views.load_snapshot import *
from warehouse.views.website import *

app_name = 'warehouse'

urlpatterns = [
    # Product URLs
    path('manage-products/', ProductListView.as_view(), name='product_list'),
    path('manage-products/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path("manage-product-image/<int:image_id>/", ProductImageDetailView.as_view(), name="product_image_detail"),

    # Product Category URLs
    path('manage-categories/', CategoryListView.as_view(), name='category_list'),
    path('manage-categories/<int:category_id>/', CategoryDetailView.as_view(), name='category_detail'),

    # Warehouse loader URLs
    path('manage-load-snapshot/', InventoryUploadView.as_view(), name='inventory_upload'),

    # Website URLs
    path('products/', VisibleProductsListView.as_view(), name='product_list_website'),
]