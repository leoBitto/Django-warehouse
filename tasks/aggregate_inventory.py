from inventory.models.base import Product, ProductCategory
from inventory.models.aggregated import InventoryGlobalAnnualAggregation, InventoryGlobalQuarterlyAggregation
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger('tasks')

def calculate_inventory_aggregates():
    # Recupera tutte le categorie e i prodotti
    categories = ProductCategory.objects.all()
    products = Product.objects.all()

    # Crea i dizionari per i conteggi e i valori dell'inventario
    products_count_by_category = {category.name: 0 for category in categories}
    inventory_value_by_category = {category.name: 0 for category in categories}

    total_products_count = 0
    total_inventory_value = 0


    # Calcola il conteggio dei prodotti per categoria e il valore dell'inventario
    for category in categories:
        category_products = products.filter(category=category)

        # Conteggio dei prodotti
        products_count = category_products.count()
        products_count_by_category[category.name] = products_count
        total_products_count += products_count

        # Calcolo del valore dell'inventario per categoria
        total_value = 0
        for product in category_products:
            # Assumiamo che average_sales_price e stock_quantity siano disponibili
            total_value += product.average_sales_price * product.stock_quantity
        
        inventory_value_by_category[category.name] = total_value
        total_inventory_value += total_value

    # Conteggio dei prodotti distinti con quantità in stock maggiore di zero
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
