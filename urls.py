# inventory/urls.py

from django.urls import path
from .views.base import *
from .views.aggregated import *

app_name = 'warehouse'

urlpatterns = [
    path('categories/', ProductCategoryView.as_view(), name='product_category_view'),
    path('products/', ProductView.as_view(), name='product_view'),
    path('products/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('download-stock-data/', DownloadStockDataCSV.as_view(), name='download_stock_data'),
    path('sales/', SaleListView.as_view(), name='sale_list'),
    path('sale/<int:sale_id>/', SaleDetailView.as_view(), name='sale_detail'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('order/<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('invoice/<str:invoice_type>/<str:invoice_number>/', InvoiceDetailView.as_view(), name='invoice_detail'),

    path('global_report/', GlobalReportView.as_view(), name='global_report'),
    path('product_report/', ProductReportView.as_view(), name='product_report'),
    path('data_quality_report/', DataQualityReportView.as_view(), name='data_quality_report'),
    path('sales_report/', SalesReportView.as_view(), name='sales_report'),
    path('orders_report/', OrdersReportView.as_view(), name='orders_report'),

    
]
