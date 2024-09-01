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
from .views.aggregated import *

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

    path('report/global-annual/', global_annual_report, name='global_annual_report'),
    path('report/product-monthly/', product_monthly_report, name='product_monthly_report'),
    path('report/data-quality-quarterly/', data_quality_quarterly_report, name='data_quality_quarterly_report'),
    path('report/sales-daily/', sales_daily_report, name='sales_daily_report'),
    path('report/orders-annual/', orders_annual_report, name='orders_annual_report'),
    # Aggiungi altre URL per gli altri report

]
