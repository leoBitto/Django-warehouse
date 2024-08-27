import logging
from django.utils import timezone
from django.db.models import Sum, F
from django.db import transaction
from ..models.aggregated import InventoryDailyAggregation
from inventory.models.base import Product, Sale, Order

logger = logging.getLogger('app')

def aggregate_inventory_daily():
    try:
        now = timezone.now()
        date = now.date()

        # Funzione helper per aggregare dati
        def aggregate(queryset, field, filter_date_field=None, filter_date=None):
            qs = queryset
            if filter_date_field and filter_date:
                qs = qs.filter(**{filter_date_field: filter_date})
            return qs.aggregate(total=Sum(field))['total'] or 0

        # Calcola i dati di aggregazione
        distinct_products_in_stock = Product.objects.using('default').filter(stock_quantity__gt=0).count()
        total_stock_value = aggregate(Product.objects.using('default'), F('stock_quantity') * F('unit_price'))

        total_sold_units = aggregate(Sale.objects.using('default'), 'quantity', 'sale_date', date)
        total_sales_value = aggregate(Sale.objects.using('default'), F('quantity') * F('unit_price'), 'sale_date', date)

        total_pending_sales = Sale.objects.using('default').filter(status='pending', sale_date=date).count()
        total_delivered_sales = Sale.objects.using('default').filter(status='delivered', delivery_date=date).count()
        total_paid_sales = Sale.objects.using('default').filter(status='paid', payment_date=date).count()
        total_cancelled_sales = Sale.objects.using('default').filter(status='cancelled', sale_date=date).count()

        total_ordered_units = aggregate(Order.objects.using('default'), 'quantity', 'sale_date', date)
        total_orders_value = aggregate(Order.objects.using('default'), F('quantity') * F('unit_price'), 'sale_date', date)

        total_pending_orders = Order.objects.using('default').filter(status='pending', sale_date=date).count()
        total_delivered_orders = Order.objects.using('default').filter(status='delivered', delivery_date=date).count()
        total_paid_orders = Order.objects.using('default').filter(status='paid', payment_date=date).count()
        total_cancelled_orders = Order.objects.using('default').filter(status='cancelled', sale_date=date).count()

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
        with transaction.atomic(using='gold'):
            obj, created = InventoryDailyAggregation.objects.using('gold').update_or_create(
                date=date,
                defaults=inventory_aggregations
            )

        logger.info(f'Inventory daily aggregation for {date} completed successfully. Created: {created}')
    except Exception as e:
        logger.error(f'Error in inventory daily aggregation for {date}: {e}')
