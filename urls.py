from django.urls import path
from warehouse.views.base import *

app_name = 'warehouse'

urlpatterns = [
    # Product URLs
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    
    # Product Category URLs
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:category_id>/', CategoryDetailView.as_view(), name='category_detail'),
]