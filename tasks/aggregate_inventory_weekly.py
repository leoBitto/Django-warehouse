import logging
from django.utils import timezone
from django.db.models import Sum, F, Count
from django.db import transaction
from django.db.models.functions import TruncWeek
from gold_bi.models import InventoryWeeklyAggregation
from inventory.models import Product, Sale, Order

logger = logging.getLogger('gold_bi')

def aggregate_inventory_weekly():
    try:
        # Ottieni la data attuale e calcola l'inizio e la fine della settimana
        now = timezone.now()
        week_start = now - timezone.timedelta(days=now.weekday())  # Ottieni il lunedì della settimana corrente
        week_end = week_start + timezone.timedelta(days=6)  # Ottieni la domenica della settimana corrente

        # Ottieni l'anno e la settimana per l'aggregazione
        year = now.year
        week_number = now.isocalendar()[1]

        # Aggregazione dei dati di prodotto
        distinct_products_in_stock = Product.objects.using('default').filter(stock_quantity__gt=0).count()

        total_stock_value = Product.objects.using('default').aggregate(
            total_value=Sum(F('stock_quantity') * F('unit_price'))
        )['total_value'] or 0

        # Aggregazione delle vendite della settimana
        total_sold_units = Sale.objects.using('default').filter(
            sale_date__range=[week_start, week_end]
        ).aggregate(total_units=Sum('quantity'))['total_units'] or 0

        total_sales_value = Sale.objects.using('default').filter(
            sale_date__range=[week_start, week_end]
        ).aggregate(total_sales=Sum(F('quantity') * F('unit_price')))['total_sales'] or 0

        # Aggregazione dello stato delle transazioni per Sales
        total_pending_sales = Sale.objects.using('default').filter(status='pending', sale_date__range=[week_start, week_end]).count()
        total_delivered_sales = Sale.objects.using('default').filter(status='delivered', delivery_date__range=[week_start, week_end]).count()
        total_paid_sales = Sale.objects.using('default').filter(status='paid', payment_date__range=[week_start, week_end]).count()
        total_cancelled_sales = Sale.objects.using('default').filter(status='cancelled', sale_date__range=[week_start, week_end]).count()

        # Aggregazione delle unità ordinate e del loro valore
        total_ordered_units = Order.objects.using('default').filter(
            sale_date__range=[week_start, week_end]
        ).aggregate(total_units=Sum('quantity'))['total_units'] or 0

        total_orders_value = Order.objects.using('default').filter(
            sale_date__range=[week_start, week_end]
        ).aggregate(total_orders=Sum(F('quantity') * F('unit_price')))['total_orders'] or 0

        # Aggregazione dello stato delle transazioni per Orders
        total_pending_orders = Order.objects.using('default').filter(status='pending', sale_date__range=[week_start, week_end]).count()
        total_delivered_orders = Order.objects.using('default').filter(status='delivered', delivery_date__range=[week_start, week_end]).count()
        total_paid_orders = Order.objects.using('default').filter(status='paid', payment_date__range=[week_start, week_end]).count()
        total_cancelled_orders = Order.objects.using('default').filter(status='cancelled', sale_date__range=[week_start, week_end]).count()

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

        # Aggiornamento o creazione del record nel modello InventoryWeeklyAggregation
        with transaction.atomic(using='gold'):
            obj, created = InventoryWeeklyAggregation.objects.using('gold').get_or_create(
                year=year,
                week=week_number
            )
            
            # Aggiorna i campi con i valori aggregati
            for field, value in inventory_aggregations.items():
                setattr(obj, field, value)
            obj.save()

        logger.info(f'Inventory weekly aggregation for year {year} week {week_number} completed successfully.')
    except Exception as e:
        logger.error(f'Error in inventory weekly aggregation for year {year} week {week_number}: {e}')
