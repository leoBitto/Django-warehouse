# inventory/urls.py

from django.urls import path
from .views import CategoryView, ProductView, SaleView, OrderView, ProductDetailView

app_name = 'inventory'

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='category_view'),
    path('products/', ProductView.as_view(), name='product_view'),
    path('products/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('sales/', SaleView.as_view(), name='sale_view'),
    path('orders/', OrderView.as_view(), name='order_view'),
]
