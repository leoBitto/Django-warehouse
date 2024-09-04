from django.db.models import Q, Count
from django.utils import timezone
from django.db import transaction
from ..models.aggregated import DataQualityQuarterlyAggregation, DataQualityAnnualAggregation
from inventory.models.base import Product, Order, Sale
import logging

logger = logging.getLogger('tasks')

def calculate_quality_aggregates(start_date=None, end_date=None):
    # Aggregazione della qualità dei dati
    product_filters = Q(images__isnull=True) | Q(description__isnull=True) | Q(category__isnull=True)
    
    product_aggregates = Product.objects.filter(product_filters).aggregate(
        products_missing_image_count=Count('id', filter=Q(images__isnull=True)),
        products_missing_description_count=Count('id', filter=Q(description__isnull=True)),
        products_missing_both_count=Count('id', filter=Q(images__isnull=True) & Q(description__isnull=True)),
        products_missing_category_count=Count('id', filter=Q(category__isnull=True))
    )

    sales_missing_customer_count = Sale.objects.filter(
        customer__isnull=True,
        sale_date__range=[start_date, end_date]
    ).count() if start_date and end_date else 0

    orders_missing_supplier_code_count = Order.objects.filter(
        supplier_product_code__isnull=True,
        sale_date__range=[start_date, end_date]
    ).count() if start_date and end_date else 0

    orders_missing_supplier_count = Order.objects.filter(
        supplier__isnull=True,
        sale_date__range=[start_date, end_date]
    ).count() if start_date and end_date else 0

    quality_aggregations = {
        **product_aggregates,
        'sales_missing_customer_count': sales_missing_customer_count,
        'orders_missing_supplier_code_count': orders_missing_supplier_code_count,
        'orders_missing_supplier_count': orders_missing_supplier_count,
    }

    return quality_aggregations

def aggregate_quality_year():
    try:
        today = timezone.now().date()
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)

        quality_aggregations = calculate_quality_aggregates(start_date=start_of_year, end_date=end_of_year)

        with transaction.atomic():
            _, created = DataQualityAnnualAggregation.objects.using('gold').update_or_create(
                year=today.year,
                defaults=quality_aggregations
            )


        logger.info(f'Inventory quality aggregation for {today.year} completed.')
    except Exception as e:
        logger.error(f'Error in inventory quality aggregation for {today.year}: {e}', exc_info=True)

def aggregate_quality_quarter():
    try:
        today = timezone.now().date()
        quarter = (today.month - 1) // 3 + 1
        start_of_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1)
        end_of_quarter = (start_of_quarter + timezone.timedelta(days=92)).replace(day=1) - timezone.timedelta(days=1)

        quality_aggregations = calculate_quality_aggregates(start_date=start_of_quarter, end_date=end_of_quarter)

        with transaction.atomic():
            _, created = DataQualityQuarterlyAggregation.objects.using('gold').update_or_create(
                year=today.year,
                quarter=quarter,
                defaults=quality_aggregations
            )

        logger.info(f'Inventory quality aggregation for {today.year} quarter {quarter} completed.')
    except Exception as e:
        logger.error(f'Error in inventory quality aggregation for {today.year} quarter {quarter}: {e}', exc_info=True)
