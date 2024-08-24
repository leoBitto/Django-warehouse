import logging
from django.utils import timezone
from django.db.models import Sum, F, Count
from django.db import transaction
from ..models.aggregated import InventoryQuarterlyAggregation
from inventory.models.base import Product, Sale, Order

logger = logging.getLogger('app')

def aggregate_inventory_quarterly():
    try:
        # Ottieni la data attuale
        now = timezone.now()
        year = now.year
        month = now.month

        # Determina il trimestre corrente
        if 1 <= month <= 3:
            quarter = 1
            start_date = timezone.datetime(year, 1, 1)
            end_date = timezone.datetime(year, 3, 31)
        elif 4 <= month <= 6:
            quarter = 2
            start_date = timezone.datetime(year, 4, 1)
            end_date = timezone.datetime(year, 6, 30)
        elif 7 <= month <= 9:
            quarter = 3
            start_date = timezone.datetime(year, 7, 1)
            end_date = timezone.datetime(year, 9, 30)
        else:
            quarter = 4
            start_date = timezone.datetime(year, 10, 1)
            end_date = timezone.datetime(year, 12, 31)

        # Aggregazione dei dati di prodotto
        distinct_products_in_stock = Product.objects.using('default').filter(stock_quantity__gt=0).count()

        total_stock_value = Product.objects.using('default').aggregate(
            total_value=Sum(F('stock_quantity') * F('unit_price'))
        )['total_value'] or 0

        # Aggregazione delle vendite del trimestre
        total_sold_units = Sale.objects.using('default').filter(
            sale_date__range=[start_date, end_date]
        ).aggregate(total_units=Sum('quantity'))['total_units'] or 0

        total_sales_value = Sale.objects.using('default').filter(
            sale_date__range=[start_date, end_date]
        ).aggregate(total_sales=Sum(F('quantity') * F('unit_price')))['total_sales'] or 0

        # Aggregazione dello stato delle transazioni per Sales
        total_pending_sales = Sale.objects.using('default').filter(status='pending', sale_date__range=[start_date, end_date]).count()
        total_delivered_sales = Sale.objects.using('default').filter(status='delivered', delivery_date__range=[start_date, end_date]).count()
        total_paid_sales = Sale.objects.using('default').filter(status='paid', payment_date__range=[start_date, end_date]).count()
        total_cancelled_sales = Sale.objects.using('default').filter(status='cancelled', sale_date__range=[start_date, end_date]).count()

        # Aggregazione delle unità ordinate e del loro valore
        total_ordered_units = Order.objects.using('default').filter(
            sale_date__range=[start_date, end_date]
        ).aggregate(total_units=Sum('quantity'))['total_units'] or 0

        total_orders_value = Order.objects.using('default').filter(
            sale_date__range=[start_date, end_date]
        ).aggregate(total_orders=Sum(F('quantity') * F('unit_price')))['total_orders'] or 0

        # Aggregazione dello stato delle transazioni per Orders
        total_pending_orders = Order.objects.using('default').filter(status='pending', sale_date__range=[start_date, end_date]).count()
        total_delivered_orders = Order.objects.using('default').filter(status='delivered', delivery_date__range=[start_date, end_date]).count()
        total_paid_orders = Order.objects.using('default').filter(status='paid', payment_date__range=[start_date, end_date]).count()
        total_cancelled_orders = Order.objects.using('default').filter(status='cancelled', sale_date__range=[start_date, end_date]).count()

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

        # Aggiornamento o creazione del record nel modello InventoryQuarterlyAggregation
        with transaction.atomic(using='gold'):
            obj, created = InventoryQuarterlyAggregation.objects.using('gold').get_or_create(
                year=year,
                quarter=quarter
            )
            
            # Aggiorna i campi con i valori aggregati
            for field, value in inventory_aggregations.items():
                setattr(obj, field, value)
            obj.save()

        logger.info(f'Inventory quarterly aggregation for {year}-Q{quarter} completed successfully.')
    except Exception as e:
        logger.error(f'Error in inventory quarterly aggregation for {year}-Q{quarter}: {e}')
