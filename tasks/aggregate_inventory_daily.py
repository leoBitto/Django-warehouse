import logging
from django.utils import timezone
from django.db.models import Sum, F, Count
from django.db import transaction
from gold_bi.models import InventoryDailyAggregation
from inventory.models import Product, Sale, Order

logger = logging.getLogger('gold_bi')

def aggregate_inventory_daily():
    try:
        # Ottieni la data di oggi (fine giornata)
        now = timezone.now()
        date = now.date()

        # Aggregazione dei dati di prodotto
        distinct_products_in_stock = Product.objects.using('default').filter(stock_quantity__gt=0).count()

        total_stock_value = Product.objects.using('default').aggregate(
            total_value=Sum(F('stock_quantity') * F('unit_price'))
        )['total_value'] or 0

        # Aggregazione delle vendite del giorno
        total_sold_units = Sale.objects.using('default').filter(
            sale_date=date
        ).aggregate(total_units=Sum('quantity'))['total_units'] or 0

        total_sales_value = Sale.objects.using('default').filter(
            sale_date=date
        ).aggregate(total_sales=Sum(F('quantity') * F('unit_price')))['total_sales'] or 0

        # Aggregazione dello stato delle transazioni per Sales
        total_pending_sales = Sale.objects.using('default').filter(status='pending', sale_date=date).count()
        total_delivered_sales = Sale.objects.using('default').filter(status='delivered', delivery_date=date).count()
        total_paid_sales = Sale.objects.using('default').filter(status='paid', payment_date=date).count()
        total_cancelled_sales = Sale.objects.using('default').filter(status='cancelled', sale_date=date).count()

        # Aggregazione delle unità ordinate e del loro valore
        total_ordered_units = Order.objects.using('default').filter(
            sale_date=date
        ).aggregate(total_units=Sum('quantity'))['total_units'] or 0

        total_orders_value = Order.objects.using('default').filter(
            sale_date=date
        ).aggregate(total_orders=Sum(F('quantity') * F('unit_price')))['total_orders'] or 0

        # Aggregazione dello stato delle transazioni per Orders
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
            obj, created = InventoryDailyAggregation.objects.using('gold').get_or_create(
                date=date
            )
            
            # Aggiorna i campi con i valori aggregati
            for field, value in inventory_aggregations.items():
                setattr(obj, field, value)
            obj.save()

        logger.info(f'Inventory daily aggregation for {date} completed successfully.')
    except Exception as e:
        logger.error(f'Error in inventory daily aggregation for {date}: {e}')
