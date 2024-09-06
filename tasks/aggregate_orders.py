import logging
from django.db import transaction
from django.db.models import Avg, Count, Sum, F, ExpressionWrapper, DecimalField
from inventory.models.base import Order
from inventory.models.aggregated import (
    OrdersDailyAggregation, OrdersWeeklyAggregation, OrdersMonthlyAggregation, 
    OrdersQuarterlyAggregation, OrdersAnnualAggregation
)
from .utils import *

logger = logging.getLogger('tasks')


def aggregate_orders(date_range):
    try:
        orders = Order.objects.filter(sale_date__range=date_range)

        total_orders_value = orders.aggregate(
            total_value=Sum(ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField()))
        )['total_value'] or 0
        orders_pending_count = orders.filter(status='pending').count()
        orders_sold_count = orders.filter(status='sold').count()
        orders_delivered_count = orders.filter(status='delivered').count()
        orders_paid_count = orders.filter(status='paid').count()
        orders_cancelled_count = orders.filter(status='cancelled').count()

        days_between_order_and_delivery = orders.exclude(delivery_date__isnull=True).aggregate(
            avg_days=Avg(F('delivery_date') - F('sale_date'))
        )['avg_days']
        days_between_order_and_delivery = days_between_order_and_delivery.days if days_between_order_and_delivery else 0

        days_between_order_and_payment = orders.exclude(payment_date__isnull=True).aggregate(
            avg_days=Avg(F('payment_date') - F('sale_date'))
        )['avg_days']
        days_between_order_and_payment = days_between_order_and_payment.days if days_between_order_and_payment else 0

        suppliers_count = orders.aggregate(Count('supplier', distinct=True))['supplier__count'] or 0
        ordered_products_count = orders.aggregate(Sum('quantity'))['quantity__sum'] or 0

        average_order_value = total_orders_value / orders_sold_count if orders_sold_count else 0

        return {
            'total_orders_value': total_orders_value,
            'orders_pending_count': orders_pending_count,
            'orders_sold_count': orders_sold_count,
            'orders_delivered_count': orders_delivered_count,
            'orders_paid_count': orders_paid_count,
            'orders_cancelled_count': orders_cancelled_count,
            'days_between_order_and_delivery': days_between_order_and_delivery,
            'days_between_order_and_payment': days_between_order_and_payment,
            'suppliers_count': suppliers_count,
            'ordered_products_count': ordered_products_count,
            'average_order_value': average_order_value,
        }

    except Exception as e:
        logger.error(f"Errore durante l'aggregazione degli ordini: {e}", exc_info=True)


# Funzioni specifiche di aggregazione
def aggregate_orders_daily():
    today = get_today()
    date_range = [today, today]

    with transaction.atomic():
        OrdersDailyAggregation.objects.using('gold').update_or_create(
            date=today,
            defaults=aggregate_orders(date_range=date_range)
        )

    logger.info(f'Aggregazione giornaliera degli ordini completata per il giorno {today}.')

def aggregate_orders_weekly():
    today = get_today()
    date_params, date_range = get_week_params(today)

    with transaction.atomic():
        OrdersWeeklyAggregation.objects.using('gold').update_or_create(
            year=date_params['year'],
            week=date_params['week'],
            defaults=aggregate_orders(date_range=date_range)
        )

    logger.info(f'Aggregazione settimanale degli ordini completata per la settimana {date_params["week"]}, {date_params["year"]}.')

def aggregate_orders_monthly():
    today = get_today()
    date_params, date_range = get_month_params(today)

    with transaction.atomic():
        OrdersMonthlyAggregation.objects.using('gold').update_or_create(
            year=date_params['year'],
            month=date_params['month'],
            defaults=aggregate_orders(date_range=date_range)
        )

    logger.info(f'Aggregazione mensile degli ordini completata per il mese {date_params["month"]}, {date_params["year"]}.')

def aggregate_orders_quarterly():
    today = get_today()
    date_params, date_range = get_quarter_params(today)

    with transaction.atomic():
        OrdersQuarterlyAggregation.objects.using('gold').update_or_create(
            year=date_params['year'],
            quarter=date_params['quarter'],
            defaults=aggregate_orders(date_range=date_range)
        )

    logger.info(f'Aggregazione trimestrale degli ordini completata per il trimestre {date_params["quarter"]}, {date_params["year"]}.')

def aggregate_orders_annually():
    today = get_today()
    date_params, date_range = get_year_params(today)

    with transaction.atomic():
        OrdersAnnualAggregation.objects.using('gold').update_or_create(
            year=date_params['year'],
            defaults=aggregate_orders(date_range=date_range)
        )

    logger.info(f'Aggregazione annuale degli ordini completata per l\'anno {date_params["year"]}.')
