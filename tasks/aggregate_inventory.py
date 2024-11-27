from warehouse.models.base import Product
from warehouse.models.aggregated import WarehouseGlobalAnnualAggregation, WarehouseGlobalQuarterlyAggregation
from django.utils import timezone
from django.db import transaction
import logging
from django.db.models import Avg, Count, Sum, F, ExpressionWrapper, DecimalField


logger = logging.getLogger('tasks')

def calculate_warehouse_aggregates():
    # Recupera tutte le categorie e i prodotti
    products = Product.objects.all()

    # Crea i dizionari per i conteggi e i valori dell'inventario
    total_products_count = 0
    total_warehouse_value = 0
    for product in products:
        total_warehouse_value += product.average_sales_price
        total_products_count += product.stock_quantity

    # Conteggio dei prodotti distinti con quantità in stock maggiore di zero
    distinct_products_count = products.filter(stock_quantity__gt=0).count()

    return {
        'distinct_products_count': distinct_products_count,
        'total_products_count': total_products_count,
        'total_warehouse_value': total_Warehouse_value,
    }


def aggregate_warehouse_quarterly():
    try:
        today = timezone.now().date()
        quarter = (today.month - 1) // 3 + 1

        warehouse_data = calculate_warehouse_aggregates()

        with transaction.atomic():
            warehouseGlobalQuarterlyAggregation.objects.using('gold').update_or_create(
                quarter=quarter,
                year=today.year,
                defaults=Warehouse_data
            )

        logger.info(f'Aggregazione trimestrale dell\'inventario completata per {quarter}/{today.year}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione trimestrale dell\'inventario: {e}', exc_info=True)

def aggregate_warehouse_annually():
    try:
        today = timezone.now().date()

        warehouse_data = calculate_Warehouse_aggregates()

        with transaction.atomic():
            WarehouseGlobalAnnualAggregation.objects.using('gold').update_or_create(
                year=today.year,
                defaults=warehouse_data
            )

        logger.info(f'Aggregazione annuale dell\'inventario completata per {today.year}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione annuale dell\'inventario: {e}', exc_info=True)
