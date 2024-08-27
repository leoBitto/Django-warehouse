import logging
from django.utils import timezone
from django.db.models import Sum, F
from django.db import transaction
from ..models.aggregated import InventoryYearlyAggregation
from inventory.models.base import Product, Sale, Order

logger = logging.getLogger('app')


def aggregate_inventory_yearly():
    try:
        now = timezone.now()
        year_start = now.replace(month=1, day=1)
        year_end = now.replace(month=12, day=31)

        def aggregate(queryset, field):
            return queryset.filter(sale_date__year=now.year).aggregate(total=Sum(field))['total'] or 0

        # Aggrega i dati annuali
        distinct_products_in_stock = Product.objects.using('default').filter(stock_quantity__gt=0).count()
        total_stock_value = aggregate(Product.objects.using('default'), F('stock_quantity') * F('unit_price'))

        total_sold_units = aggregate(Sale.objects.using('default'), 'quantity')
        total_sales_value = aggregate(Sale.objects.using('default'), F('quantity') * F('unit_price'))

        total_pending_sales = Sale.objects.using('default').filter(status='pending', sale_date__range=[year_start, year_end]).count()
        total_delivered_sales = Sale.objects.using('default').filter(status='delivered', delivery_date__range=[year_start, year_end]).count()
        total_paid_sales = Sale.objects.using('default').filter(status='paid', payment_date__range=[year_start, year_end]).count()
        total_cancelled_sales = Sale.objects.using('default').filter(status='cancelled', sale_date__range=[year_start, year_end]).count()

        total_ordered_units = aggregate(Order.objects.using('default'), 'quantity')
        total_orders_value = aggregate(Order.objects.using('default'), F('quantity') * F('unit_price'))

        total_pending_orders = Order.objects.using('default').filter(status='pending', sale_date__range=[year_start, year_end]).count()
        total_delivered_orders = Order.objects.using('default').filter(status='delivered', delivery_date__range=[year_start, year_end]).count()
        total_paid_orders = Order.objects.using('default').filter(status='paid', payment_date__range=[year_start, year_end]).count()
        total_cancelled_orders = Order.objects.using('default').filter(status='cancelled', sale_date__range=[year_start, year_end]).count()

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
            obj, created = InventoryYearlyAggregation.objects.using('gold').update_or_create(
                year=now.year,
                defaults=inventory_aggregations
            )

        logger.info(f'Inventory yearly aggregation for {now.year} completed successfully. Created: {created}')
    except Exception as e:
        logger.error(f'Error in inventory yearly aggregation for {now.year}: {e}')
