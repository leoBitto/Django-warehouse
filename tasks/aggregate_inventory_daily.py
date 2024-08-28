import logging
from django.utils import timezone
from django.db.models import Sum
from django.db import transaction
from decimal import Decimal
from ..models.aggregated import InventoryDailyAggregation
from inventory.models.base import Product, Sale, Order

logger = logging.getLogger('app')

def aggregate_inventory_daily():
    try:
        now = timezone.now()
        date = now.date()

        # Calcola il numero di prodotti distinti in stock
        distinct_products_in_stock = Product.objects.filter(stock_quantity__gt=0).count()

        # Calcola il valore totale delle scorte
        total_stock_value = Decimal('0')
        for product in Product.objects.filter(stock_quantity__gt=0):
            total_stock_value += product.stock_quantity * product.average_sales_price

        # Calcola le vendite
        total_sold_units = Sale.objects.filter(sale_date=date).aggregate(total=Sum('quantity'))['total'] or 0
        total_sales_value = Decimal('0')
        for sale in Sale.objects.filter(sale_date=date):
            total_sales_value += sale.quantity * sale.unit_price

        # Calcola gli ordini
        total_ordered_units = Order.objects.filter(sale_date=date).aggregate(total=Sum('quantity'))['total'] or 0
        total_orders_value = Decimal('0')
        for order in Order.objects.filter(sale_date=date):
            total_orders_value += order.quantity * order.unit_price

        # Calcola i contatori degli stati delle vendite e degli ordini
        total_pending_sales = Sale.objects.filter(status='pending', sale_date=date).count()
        total_delivered_sales = Sale.objects.filter(status='delivered', delivery_date=date).count()
        total_paid_sales = Sale.objects.filter(status='paid', payment_date=date).count()
        total_cancelled_sales = Sale.objects.filter(status='cancelled', sale_date=date).count()

        total_pending_orders = Order.objects.filter(status='pending', sale_date=date).count()
        total_delivered_orders = Order.objects.filter(status='delivered', delivery_date=date).count()
        total_paid_orders = Order.objects.filter(status='paid', payment_date=date).count()
        total_cancelled_orders = Order.objects.filter(status='cancelled', sale_date=date).count()

        # Creazione del dizionario per l'aggregazione
        inventory_aggregations = {
            'distinct_products_in_stock': distinct_products_in_stock,
            'total_stock_value': total_stock_value,
            'total_sold_units': total_sold_units,
            'total_sales_value': total_sales_value,
            'total_pending_sales': total_pending_sales,
            'total_delivered_sales': total_delivered_sales,
            'total_paid_sales': total_paid_sales,
            'total_cancelled_sales': total_cancelled_sales,
            'total_ordered_units': total_ordered_units,
            'total_orders_value': total_orders_value,
            'total_pending_orders': total_pending_orders,
            'total_delivered_orders': total_delivered_orders,
            'total_paid_orders': total_paid_orders,
            'total_cancelled_orders': total_cancelled_orders,
        }

        # Aggiornamento o creazione del record nel modello InventoryDailyAggregation
        with transaction.atomic():
            obj, created = InventoryDailyAggregation.objects.using('gold').update_or_create(
                date=date,
                defaults=inventory_aggregations
            )

        logger.info(f'Inventory daily aggregation for {date} completed successfully. Created: {created}')
    except Exception as e:
        logger.error(f'Error in inventory daily aggregation for {date}: {e}')
