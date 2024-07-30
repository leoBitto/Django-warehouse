# inventory/urls.py

from django.urls import path
from .views import CategoryView, ProductView, SaleView, OrderView

app_name = 'inventory'

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='category_view'),
    path('products/', ProductView.as_view(), name='product_view'),
    path('sales/', SaleView.as_view(), name='sale_view'),
    path('orders/', OrderView.as_view(), name='order_view'),
]
