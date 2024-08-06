import logging
from django.utils import timezone
from django.db.models import Sum, F
from django.db import transaction
from inventory.models import Product
from gold_bi.models import InventoryMonthlySnapshot

logger = logging.getLogger('gold_bi')

def aggregate_inventory_snapshot_monthly():
    try:
        # Ottieni la data corrente
        now = timezone.now()
        date = now.date()
        
        # Calcola l'inizio e la fine del mese corrente
        start_of_month = date.replace(day=1)
        end_of_month = (start_of_month.replace(day=28) + timezone.timedelta(days=4)).replace(day=1) - timezone.timedelta(days=1)

        year = start_of_month.year
        month = start_of_month.month

        # Aggregazione globale del magazzino
        total_stock_quantity = Product.objects.using('default').aggregate(
            total_quantity=Sum('stock_quantity')
        )['total_quantity'] or 0

        total_stock_value = Product.objects.using('default').aggregate(
            total_value=Sum(F('stock_quantity') * F('unit_price'))
        )['total_value'] or 0

        total_number_of_products = Product.objects.using('default').count()
        average_stock_per_product = (total_stock_quantity / total_number_of_products) if total_number_of_products > 0 else 0

        # Creazione del dizionario per l'aggregazione
        monthly_aggregations = {
            'total_products': total_number_of_products,
            'total_stock_quantity': total_stock_quantity,
            'total_stock_value': total_stock_value,
            'average_stock_per_product': average_stock_per_product,
        }

        # Aggiornamento o creazione del record nel modello InventoryMonthlySnapshot
        with transaction.atomic(using='gold'):
            obj, created = InventoryMonthlySnapshot.objects.using('gold').get_or_create(
                month=month,
                year=year
            )
            
            # Aggiorna i campi con i valori aggregati
            for field, value in monthly_aggregations.items():
                setattr(obj, field, value)
            obj.save()

        logger.info(f'Inventory monthly snapshot for {year}-{month} completed successfully.')
    except Exception as e:
        logger.error(f'Error in inventory monthly snapshot for {year}-{month}: {e}')
