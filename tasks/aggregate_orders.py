import logging
from django.utils import timezone
from django.db import transaction
from django.db.models import Avg, Count, Sum, F
from inventory.models.base import Order
from inventory.models.aggregated import (
    OrdersDailyAggregation, OrdersWeeklyAggregation, OrdersMonthlyAggregation, 
    OrdersQuarterlyAggregation, OrdersAnnualAggregation
)


logger = logging.getLogger('app')

def aggregate_orders_daily():
    try:
        today = timezone.now().date()

        # Recupero degli ordini del giorno corrente
        orders = Order.objects.filter(sale_date__date=today)

        # Aggregazione delle metriche
        total_orders_value = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        orders_pending_count = orders.filter(status='pending').count()
        orders_sold_count = orders.filter(status='sold').count()
        orders_delivered_count = orders.filter(status='delivered').count()
        orders_paid_count = orders.filter(status='paid').count()
        orders_cancelled_count = orders.filter(status='cancelled').count()

        days_between_order_and_delivery = orders.exclude(delivery_date__isnull=True).aggregate(
            Avg(F('delivery_date') - F('sale_date'))
        )['delivery_date__sale_date__avg'].days or 0

        days_between_order_and_payment = orders.exclude(payment_date__isnull=True).aggregate(
            Avg(F('payment_date') - F('sale_date'))
        )['payment_date__sale_date__avg'].days or 0

        suppliers_count = orders.aggregate(Count('supplier', distinct=True))['supplier__count'] or 0
        ordered_products_count = orders.aggregate(Sum('quantity'))['quantity__sum'] or 0

        ordered_products_count_by_category = orders.values('product__category').annotate(
            total_ordered=Sum('quantity')
        )

        gross_margin = orders.aggregate(
            gross_margin=Sum(F('total_price') - F('quantity') * F('product__cost'))
        )['gross_margin'] or 0

        average_order_value = total_orders_value / orders_sold_count if orders_sold_count else 0

        with transaction.atomic():
            OrdersDailyAggregation.objects.using('gold').update_or_create(
                date=today,
                defaults={
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
                    'ordered_products_count_by_category': ordered_products_count_by_category,
                    'gross_margin': gross_margin,
                    'average_order_value': average_order_value,
                }
            )

        logger.info(f'Aggregazione giornaliera degli ordini completata per il giorno {today}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione giornaliera degli ordini per il giorno {today}: {e}')


def aggregate_orders_weekly():
    try:
        today = timezone.now().date()
        start_of_week = today - timezone.timedelta(days=today.weekday())
        end_of_week = start_of_week + timezone.timedelta(days=6)

        # Recupero degli ordini della settimana corrente
        orders = Order.objects.filter(sale_date__range=[start_of_week, end_of_week])

        # Aggregazione delle metriche
        total_orders_value = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        orders_pending_count = orders.filter(status='pending').count()
        orders_sold_count = orders.filter(status='sold').count()
        orders_delivered_count = orders.filter(status='delivered').count()
        orders_paid_count = orders.filter(status='paid').count()
        orders_cancelled_count = orders.filter(status='cancelled').count()

        days_between_order_and_delivery = orders.exclude(delivery_date__isnull=True).aggregate(
            Avg(F('delivery_date') - F('sale_date'))
        )['delivery_date__sale_date__avg'].days or 0

        days_between_order_and_payment = orders.exclude(payment_date__isnull=True).aggregate(
            Avg(F('payment_date') - F('sale_date'))
        )['payment_date__sale_date__avg'].days or 0

        suppliers_count = orders.aggregate(Count('supplier', distinct=True))['supplier__count'] or 0
        ordered_products_count = orders.aggregate(Sum('quantity'))['quantity__sum'] or 0

        ordered_products_count_by_category = orders.values('product__category').annotate(
            total_ordered=Sum('quantity')
        )

        gross_margin = orders.aggregate(
            gross_margin=Sum(F('total_price') - F('quantity') * F('product__cost'))
        )['gross_margin'] or 0

        average_order_value = total_orders_value / orders_sold_count if orders_sold_count else 0

        with transaction.atomic():
            OrdersWeeklyAggregation.objects.using('gold').update_or_create(
                start_date=start_of_week,
                defaults={
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
                    'ordered_products_count_by_category': ordered_products_count_by_category,
                    'gross_margin': gross_margin,
                    'average_order_value': average_order_value,
                }
            )

        logger.info(f'Aggregazione settimanale degli ordini completata per la settimana {start_of_week} - {end_of_week}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione settimanale degli ordini per la settimana {start_of_week} - {end_of_week}: {e}')

def aggregate_orders_monthly():
    try:
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)

        # Recupero degli ordini del mese corrente
        orders = Order.objects.filter(sale_date__range=[start_of_month, end_of_month])

        # Aggregazione delle metriche
        total_orders_value = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        orders_pending_count = orders.filter(status='pending').count()
        orders_sold_count = orders.filter(status='sold').count()
        orders_delivered_count = orders.filter(status='delivered').count()
        orders_paid_count = orders.filter(status='paid').count()
        orders_cancelled_count = orders.filter(status='cancelled').count()

        days_between_order_and_delivery = orders.exclude(delivery_date__isnull=True).aggregate(
            Avg(F('delivery_date') - F('sale_date'))
        )['delivery_date__sale_date__avg'].days or 0

        days_between_order_and_payment = orders.exclude(payment_date__isnull=True).aggregate(
            Avg(F('payment_date') - F('sale_date'))
        )['payment_date__sale_date__avg'].days or 0

        suppliers_count = orders.aggregate(Count('supplier', distinct=True))['supplier__count'] or 0
        ordered_products_count = orders.aggregate(Sum('quantity'))['quantity__sum'] or 0

        ordered_products_count_by_category = orders.values('product__category').annotate(
            total_ordered=Sum('quantity')
        )

        gross_margin = orders.aggregate(
            gross_margin=Sum(F('total_price') - F('quantity') * F('product__cost'))
        )['gross_margin'] or 0

        average_order_value = total_orders_value / orders_sold_count if orders_sold_count else 0

        with transaction.atomic():
            OrdersMonthlyAggregation.objects.using('gold').update_or_create(
                start_date=start_of_month,
                defaults={
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
                    'ordered_products_count_by_category': ordered_products_count_by_category,
                    'gross_margin': gross_margin,
                    'average_order_value': average_order_value,
                }
            )

        logger.info(f'Aggregazione mensile degli ordini completata per il mese {start_of_month}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione mensile degli ordini per il mese {start_of_month}: {e}')


def aggregate_orders_quarterly():
    try:
        today = timezone.now().date()
        quarter = (today.month - 1) // 3 + 1
        start_of_quarter = timezone.datetime(today.year, 3 * quarter - 2, 1).date()
        end_of_quarter = (timezone.datetime(today.year, 3 * quarter + 1, 1) - timezone.timedelta(days=1)).date()

        # Recupero degli ordini del trimestre corrente
        orders = Order.objects.filter(sale_date__range=[start_of_quarter, end_of_quarter])

        # Aggregazione delle metriche
        total_orders_value = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        orders_pending_count = orders.filter(status='pending').count()
        orders_sold_count = orders.filter(status='sold').count()
        orders_delivered_count = orders.filter(status='delivered').count()
        orders_paid_count = orders.filter(status='paid').count()
        orders_cancelled_count = orders.filter(status='cancelled').count()

        days_between_order_and_delivery = orders.exclude(delivery_date__isnull=True).aggregate(
            Avg(F('delivery_date') - F('sale_date'))
        )['delivery_date__sale_date__avg'].days or 0

        days_between_order_and_payment = orders.exclude(payment_date__isnull=True).aggregate(
            Avg(F('payment_date') - F('sale_date'))
        )['payment_date__sale_date__avg'].days or 0

        suppliers_count = orders.aggregate(Count('supplier', distinct=True))['supplier__count'] or 0
        ordered_products_count = orders.aggregate(Sum('quantity'))['quantity__sum'] or 0

        ordered_products_count_by_category = orders.values('product__category').annotate(
            total_ordered=Sum('quantity')
        )

        gross_margin = orders.aggregate(
            gross_margin=Sum(F('total_price') - F('quantity') * F('product__cost'))
        )['gross_margin'] or 0

        average_order_value = total_orders_value / orders_sold_count if orders_sold_count else 0

        with transaction.atomic():
            OrdersQuarterlyAggregation.objects.using('gold').update_or_create(
                start_date=start_of_quarter,
                defaults={
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
                    'ordered_products_count_by_category': ordered_products_count_by_category,
                    'gross_margin': gross_margin,
                    'average_order_value': average_order_value,
                }
            )

        logger.info(f'Aggregazione trimestrale degli ordini completata per il trimestre {quarter}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione trimestrale degli ordini per il trimestre {quarter}: {e}')


def aggregate_orders_annually():
    try:
        today = timezone.now().date()
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)

        # Recupero degli ordini dell'anno corrente
        orders = Order.objects.filter(sale_date__range=[start_of_year, end_of_year])

        # Aggregazione delle metriche
        total_orders_value = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        orders_pending_count = orders.filter(status='pending').count()
        orders_sold_count = orders.filter(status='sold').count()
        orders_delivered_count = orders.filter(status='delivered').count()
        orders_paid_count = orders.filter(status='paid').count()
        orders_cancelled_count = orders.filter(status='cancelled').count()

        days_between_order_and_delivery = orders.exclude(delivery_date__isnull=True).aggregate(
            Avg(F('delivery_date') - F('sale_date'))
        )['delivery_date__sale_date__avg'].days or 0

        days_between_order_and_payment = orders.exclude(payment_date__isnull=True).aggregate(
            Avg(F('payment_date') - F('sale_date'))
        )['payment_date__sale_date__avg'].days or 0

        suppliers_count = orders.aggregate(Count('supplier', distinct=True))['supplier__count'] or 0
        ordered_products_count = orders.aggregate(Sum('quantity'))['quantity__sum'] or 0

        ordered_products_count_by_category = orders.values('product__category').annotate(
            total_ordered=Sum('quantity')
        )

        gross_margin = orders.aggregate(
            gross_margin=Sum(F('total_price') - F('quantity') * F('product__cost'))
        )['gross_margin'] or 0

        average_order_value = total_orders_value / orders_sold_count if orders_sold_count else 0

        with transaction.atomic():
            OrdersAnnualAggregation.objects.using('gold').update_or_create(
                start_date=start_of_year,
                defaults={
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
                    'ordered_products_count_by_category': ordered_products_count_by_category,
                    'gross_margin': gross_margin,
                    'average_order_value': average_order_value,
                }
            )

        logger.info(f'Aggregazione annuale degli ordini completata per l\'anno {start_of_year.year}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione annuale degli ordini per l\'anno {start_of_year.year}: {e}')
