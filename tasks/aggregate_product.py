from django.db.models import Count, Sum
from django.utils import timezone
from django.db import transaction
from inventory.models.base import Product, Order, Sale
from inventory.models.aggregated import ProductAnnualAggregation, ProductQuarterlyAggregation, ProductMonthlyAggregation
import logging
from backoffice.utils import *

logger = logging.getLogger('tasks')

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

def aggregate_product_quarterly():
    today = timezone.now().date()
    quarter = (today.month - 1) // 3 + 1
    start_of_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1)
    end_of_quarter = (start_of_quarter + timezone.timedelta(days=92)).replace(day=1) - timezone.timedelta(days=1)
    
    try:
        today = timezone.now().date()
        
        for product in Product.objects.all():
            defaults = calculate_aggregations(product, start_of_quarter, end_of_quarter)
            
            with transaction.atomic():
                _, created = ProductQuarterlyAggregation.objects.using('gold').update_or_create(
                    year=today.year,
                    quarter=quarter,
                    product_name=product.name,
                    product_internal_code=product.internal_code,
                    defaults=defaults
                )

            logger.info(f'Aggregazione trimestrale per prodotto {product} completata per il trimestre {today.year} - {quarter}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione trimestrale del prodotto {product}: {e}', exc_info=True)


def aggregate_product_annually():
    today = timezone.now().date()
    start_of_year = today.replace(month=1, day=1)
    end_of_year = today.replace(month=12, day=31)
    
    try:
        today = timezone.now().date()
        
        for product in Product.objects.all():
            defaults = calculate_aggregations(product, start_of_year, end_of_year)
            
            with transaction.atomic():
                _, created = ProductAnnualAggregation.objects.using('gold').update_or_create(
                    year=today.year,
                    product_name=product.name,
                    product_internal_code=product.internal_code,
                    defaults=defaults
                )

            logger.info(f'Aggregazione annuale per prodotto {product} completata per l\'anno  {today.year}')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione annuale del prodotto {product}: {e}', exc_info=True)


def aggregate_product_monthly():
    today = get_today()
    date_params, date_range = get_month_params(today)
    
    try:
        for product in Product.objects.all():
            defaults = calculate_aggregations(product, date_range[0], date_range[1])

            with transaction.atomic():
                _, created = ProductMonthlyAggregation.objects.using('gold').update_or_create(
                    year=date_params['year'],
                    month=date_params['month'],
                    product_name=product.name,
                    product_internal_code=product.internal_code,
                    defaults=defaults
                )

            logger.info(f'Aggregazione mensile per prodotto {product} completata per il mese {date_params["month"]} anno {date_params["year"]}')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione mensile del prodotto {product}: {e}', exc_info=True)

