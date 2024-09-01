from django.db.models import Count, Sum
from django.utils import timezone
from django.db import transaction
from inventory.models.base import Product, Order, Sale
from inventory.models.aggregated import ProductAnnualAggregation, ProductQuarterlyAggregation, ProductMonthlyAggregation
import logging

logger = logging.getLogger('app')

def calculate_aggregations(product, start_date, end_date):
    orders = Order.objects.filter(sale_date__range=[start_date, end_date], product=product)
    sales = Sale.objects.filter(sale_date__range=[start_date, end_date], product=product)
    
    suppliers_count = orders.values('supplier').distinct().count()
    customers_count = sales.values('customer').distinct().count()
    
    return {
        'product_quantity': product.stock_quantity,
        'total_product_value': product.stock_quantity * product.average_sales_price,
        'gross_margin': ((product.average_sales_price - product.average_purchase_price) / product.average_sales_price) * 100 if product.average_sales_price else 0,
        'suppliers_count': suppliers_count,
        'customers_count': customers_count,
    }

def aggregate_product_period(aggregation_model, start_date, end_date, period_name):
    try:
        today = timezone.now().date()
        
        for product in Product.objects.all():
            defaults = calculate_aggregations(product, start_date, end_date)
            
            with transaction.atomic():
                aggregation_model.objects.using('gold').update_or_create(
                    product=product,
                    year=today.year,
                    defaults=defaults
                )
            
            logger.info(f'Aggregazione {period_name} per prodotto {product} completata per il periodo {start_date} - {end_date}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione {period_name} del prodotto {product}: {e}', exc_info=True)

def aggregate_product_quarter():
    today = timezone.now().date()
    quarter = (today.month - 1) // 3 + 1
    start_of_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1)
    end_of_quarter = (start_of_quarter + timezone.timedelta(days=92)).replace(day=1) - timezone.timedelta(days=1)
    
    aggregate_product_period(ProductQuarterlyAggregation, start_of_quarter, end_of_quarter, "trimestrale")

def aggregate_product_year():
    today = timezone.now().date()
    start_of_year = today.replace(month=1, day=1)
    end_of_year = today.replace(month=12, day=31)
    
    aggregate_product_period(ProductAnnualAggregation, start_of_year, end_of_year, "annuale")

def aggregate_product_month():
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timezone.timedelta(days=31)).replace(day=1) - timezone.timedelta(days=1)
    
    aggregate_product_period(ProductMonthlyAggregation, start_of_month, end_of_month, "mensile")
