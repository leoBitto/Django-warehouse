from ..models.aggregated import InventoryWeeklyAggregation
import logging
from django.utils import timezone
from django.db.models import Sum, F
from django.db import transaction
from inventory.models.base import Product, Sale, Order

logger = logging.getLogger('app')

def aggregate_inventory_weekly():
    try:
        now = timezone.now()
        week_start = now - timezone.timedelta(days=now.weekday())
        week_end = week_start + timezone.timedelta(days=6)

        # Logica simile al task giornaliero, ma filtrando tra week_start e week_end
        def aggregate(queryset, field):
            return queryset.filter(sale_date__range=[week_start, week_end]).aggregate(total=Sum(field))['total'] or 0

        # Aggrega i dati settimanali
        distinct_products_in_stock = Product.objects.using('default').filter(stock_quantity__gt=0).count()
        total_stock_value = aggregate(Product.objects.using('default'), F('stock_quantity') * F('unit_price'))

        total_sold_units = aggregate(Sale.objects.using('default'), 'quantity')
        total_sales_value = aggregate(Sale.objects.using('default'), F('quantity') * F('unit_price'))

        total_pending_sales = Sale.objects.using('default').filter(status='pending', sale_date__range=[week_start, week_end]).count()
        total_delivered_sales = Sale.objects.using('default').filter(status='delivered', delivery_date__range=[week_start, week_end]).count()
        total_paid_sales = Sale.objects.using('default').filter(status='paid', payment_date__range=[week_start, week_end]).count()
        total_cancelled_sales = Sale.objects.using('default').filter(status='cancelled', sale_date__range=[week_start, week_end]).count()

        total_ordered_units = aggregate(Order.objects.using('default'), 'quantity')
        total_orders_value = aggregate(Order.objects.using('default'), F('quantity') * F('unit_price'))

        total_pending_orders = Order.objects.using('default').filter(status='pending', sale_date__range=[week_start, week_end]).count()
        total_delivered_orders = Order.objects.using('default').filter(status='delivered', delivery_date__range=[week_start, week_end]).count()
        total_paid_orders = Order.objects.using('default').filter(status='paid', payment_date__range=[week_start, week_end]).count()
        total_cancelled_orders = Order.objects.using('default').filter(status='cancelled', sale_date__range=[week_start, week_end]).count()

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

        with transaction.atomic(using='gold'):
            obj, created = InventoryWeeklyAggregation.objects.using('gold').update_or_create(
                week=week_start.isocalendar()[1],
                defaults=inventory_aggregations
            )

        logger.info(f'Inventory weekly aggregation for week {week_start.isocalendar()[1]} completed successfully. Created: {created}')
    except Exception as e:
        logger.error(f'Error in inventory weekly aggregation: {e}')
