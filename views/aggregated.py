# inventory/views/aggregated.py
from django.shortcuts import render
from inventory.models.aggregated import (
    InventoryGlobalAnnualAggregation, ProductMonthlyAggregation,
    DataQualityQuarterlyAggregation, SalesDailyAggregation,
    OrdersAnnualAggregation
)

def global_annual_report(request):
    data = InventoryGlobalAnnualAggregation.objects.all()
    return render(request, 'inventory/reports/global_annual_report.html', {'data': data})

def product_monthly_report(request):
    data = ProductMonthlyAggregation.objects.all()
    return render(request, 'inventory/reports/product_monthly_report.html', {'data': data})

def data_quality_quarterly_report(request):
    data = DataQualityQuarterlyAggregation.objects.all()
    return render(request, 'inventory/reports/data_quality_quarterly_report.html', {'data': data})

def sales_daily_report(request):
    data = SalesDailyAggregation.objects.all()
    return render(request, 'inventory/reports/sales_daily_report.html', {'data': data})

def orders_annual_report(request):
    data = OrdersAnnualAggregation.objects.all()
    return render(request, 'inventory/reports/orders_annual_report.html', {'data': data})

# Aggiungi altre view per gli altri report
