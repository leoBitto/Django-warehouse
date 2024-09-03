from django.db.models import Sum, F, Count, Value
from django.db.models.functions import Coalesce
from inventory.models.base import Product, ProductCategory
from inventory.models.aggregated import InventoryGlobalAnnualAggregation, InventoryGlobalQuarterlyAggregation
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger('app')

def calculate_inventory_aggregates():
    categories = ProductCategory.objects.all()
    products = Product.objects.all()

    # Calcolo del conteggio dei prodotti e del valore dell'inventario per categoria
    inventory_data = products.values('category').annotate(
        total_count=Count('id'),
        total_value=Sum(F('average_sales_price') * F('stock_quantity'))
    )

    products_count_by_category = {category: 0 for category in categories}
    inventory_value_by_category = {category: 0 for category in categories}

    total_products_count = 0
    total_inventory_value = 0

    for data in inventory_data:
        category = ProductCategory.objects.get(pk=data['category'])
        products_count_by_category[category] = data['total_count']
        inventory_value_by_category[category] = data['total_value']
        total_products_count += data['total_count']
        total_inventory_value += data['total_value']

    distinct_products_count = products.filter(stock_quantity__gt=0).count()

    return {
        'distinct_products_count': distinct_products_count,
        'products_count_by_category': products_count_by_category,
        'total_products_count': total_products_count,
        'total_inventory_value': total_inventory_value,
        'inventory_value_by_category': inventory_value_by_category,
    }

def aggregate_inventory_quarter():
    try:
        today = timezone.now().date()
        quarter = (today.month - 1) // 3 + 1

        inventory_data = calculate_inventory_aggregates()

        with transaction.atomic():
            InventoryGlobalQuarterlyAggregation.objects.using('gold').update_or_create(
                quarter=quarter,
                year=today.year,
                defaults=inventory_data
            )

        logger.info(f'Aggregazione trimestrale dell\'inventario completata per {quarter}/{today.year}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione trimestrale dell\'inventario: {e}', exc_info=True)

def aggregate_inventory_annual():
    try:
        today = timezone.now().date()

        inventory_data = calculate_inventory_aggregates()

        with transaction.atomic():
            InventoryGlobalAnnualAggregation.objects.using('gold').update_or_create(
                year=today.year,
                defaults=inventory_data
            )

        logger.info(f'Aggregazione annuale dell\'inventario completata per {today.year}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione annuale dell\'inventario: {e}', exc_info=True)
