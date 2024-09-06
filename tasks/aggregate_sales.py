import logging
from django.db import transaction
from django.db.models import Avg, Count, Sum, F, ExpressionWrapper, DecimalField
from inventory.models.base import Sale
from inventory.models.aggregated import (
    SalesDailyAggregation, SalesWeeklyAggregation, SalesMonthlyAggregation, 
    SalesQuarterlyAggregation, SalesAnnualAggregation
)
from backoffice.utils import *
from .utils import *

logger = logging.getLogger('tasks')


def aggregate_sales(date_range):
    try:
        sales = Sale.objects.filter(sale_date__range=date_range)

        # Aggregazione delle metriche
        total_sales_value = sales.aggregate(
            total_value=Sum(ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField()))
        )['total_value'] or 0
        sales_pending_count = sales.filter(status='pending').count()
        sales_sold_count = sales.filter(status='sold').count()
        sales_delivered_count = sales.filter(status='delivered').count()
        sales_paid_count = sales.filter(status='paid').count()
        sales_cancelled_count = sales.filter(status='cancelled').count()

        days_between_sale_and_delivery = sales.exclude(delivery_date__isnull=True).aggregate(
            avg_days=Avg(F('delivery_date') - F('sale_date'))
        )['avg_days']

        # Verifica se `avg_days` è None, altrimenti accedi all'attributo `.days`.
        if days_between_sale_and_delivery is not None:
            days_between_sale_and_delivery = days_between_sale_and_delivery.days
        else:
            days_between_sale_and_delivery = 0

        days_between_sale_and_payment = sales.exclude(payment_date__isnull=True).aggregate(
            avg_days=Avg(F('payment_date') - F('sale_date'))
        )['avg_days']

        if days_between_sale_and_payment is not None:
            days_between_sale_and_payment = days_between_sale_and_payment.days
        else:
            days_between_sale_and_payment = 0

        customers_count = sales.aggregate(Count('customer', distinct=True))['customer__count'] or 0
        sold_products_count = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0

        # Calcolo del gross_margin in Python
        gross_margin = calculate_gross_margin(sales)
        
        average_sales_value = total_sales_value / sales_sold_count if sales_sold_count else 0

        defaults = {
                    'total_sales_value': total_sales_value,
                    'sales_pending_count': sales_pending_count,
                    'sales_sold_count': sales_sold_count,
                    'sales_delivered_count': sales_delivered_count,
                    'sales_paid_count': sales_paid_count,
                    'sales_cancelled_count': sales_cancelled_count,
                    'days_between_sale_and_delivery': days_between_sale_and_delivery,
                    'days_between_sale_and_payment': days_between_sale_and_payment,
                    'customers_count': customers_count,
                    'sold_products_count': sold_products_count,
                    'gross_margin': gross_margin,
                    'average_sales_value': average_sales_value,
                }
        #logger.info(f"defaults: {defaults}")
        return defaults

    except Exception as e:
        logger.error(f"Errore durante l'aggregazione: {e}", exc_info=True)


# Funzioni specifiche di aggregazione che usano la funzione generica
def aggregate_sales_daily():
    today = get_today()
    date_params = {'date': today}
    date_range = [today, today]

    with transaction.atomic():
        SalesDailyAggregation.objects.using('gold').update_or_create(
            date=date_params['date'],
            defaults=aggregate_sales(date_range=date_range)
        )

    logger.info(f'Aggregazione giornaliera delle vendite completata per il giorno {today}.')

def aggregate_sales_weekly():
    today = get_today()
    date_params, date_range = get_week_params(today)
    
    with transaction.atomic():
        SalesWeeklyAggregation.objects.using('gold').update_or_create(
            year=date_params['year'],
            week=date_params['week'],
            defaults=aggregate_sales(date_range=date_range)
        )

    logger.info(f'Aggregazione settimanale delle vendite completata per la settimana {date_params["week"]}, {date_params["year"]}.')

def aggregate_sales_monthly():
    today = get_today()
    date_params, date_range = get_month_params(today)

    with transaction.atomic():
        SalesMonthlyAggregation.objects.using('gold').update_or_create(
            year=date_params['year'],
            month=date_params['month'],
            defaults=aggregate_sales(date_range=date_range)
        )

    logger.info(f'Aggregazione mensile delle vendite completata per il mese {date_params["month"]}, {date_params["year"]}.')

def aggregate_sales_quarterly():
    today = get_today()
    date_params, date_range = get_quarter_params(today)

    with transaction.atomic():
        SalesQuarterlyAggregation.objects.using('gold').update_or_create(
            year=date_params['year'],
            quarter=date_params['quarter'],
            defaults=aggregate_sales(date_range=date_range)
        )

    logger.info(f'Aggregazione trimestrale delle vendite completata per il trimestre {date_params["quarter"]}, {date_params["year"]}.')

def aggregate_sales_annually():
    today = get_today()
    date_params, date_range = get_year_params(today)

    with transaction.atomic():
        SalesAnnualAggregation.objects.using('gold').update_or_create(
            year=date_params['year'],
            defaults=aggregate_sales(date_range=date_range)
        )

    logger.info(f'Aggregazione annuale delle vendite completata per l\'anno {date_params["year"]}.')

