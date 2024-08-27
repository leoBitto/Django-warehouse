# inventory/urls.py

from django.urls import path
from .views.base import (ProductCategoryView,
    ProductView, 
    SaleListView, 
    SaleDetailView, 
    OrderListView, 
    OrderDetailView, 
    ProductDetailView, 
    DownloadStockDataCSV,
    )
from .views.aggregated import GenerateReportView

app_name = 'inventory'

urlpatterns = [
    path('categories/', ProductCategoryView.as_view(), name='product_category_view'),
    path('products/', ProductView.as_view(), name='product_view'),
    path('products/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('download-stock-data/', DownloadStockDataCSV.as_view(), name='download_stock_data'),
    path('sales/', SaleListView.as_view(), name='sale_list'),
    path('sale/<int:sale_id>/', SaleDetailView.as_view(), name='sale_detail'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('order/<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),

    path('', GenerateReportView.as_view(), name='generate_report'),

]
