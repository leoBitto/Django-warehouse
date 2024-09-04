import logging
from django.utils import timezone
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.db.models import Avg, Count, Sum, F, ExpressionWrapper, DecimalField
from inventory.models.base import Sale
from inventory.models.aggregated import (
    SalesDailyAggregation, SalesWeeklyAggregation, SalesMonthlyAggregation, 
    SalesQuarterlyAggregation, SalesAnnualAggregation
)

logger = logging.getLogger('tasks')

def calculate_gross_margin(sales):
    total_gross_margin = 0
    for sale in sales:
        # Calcoliamo il margine lordo per ogni vendita, usando il prezzo medio d'acquisto.
        total_gross_margin = (total_gross_margin + (sale.unit_price - sale.product.average_purchase_price) )/2
    return total_gross_margin


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

        # Estrarre i prodotti venduti per categoria
        sold_products_count_by_category = list(sales.values('product__category').annotate(
            total_sold=Sum('quantity')
        ))

        # Serializzare i dati in JSON
        sold_products_count_by_category_json = json.dumps(sold_products_count_by_category, cls=DjangoJSONEncoder)

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
                    'sold_products_count_by_category': sold_products_count_by_category_json,
                    'gross_margin': gross_margin,
                    'average_sales_value': average_sales_value,
                }
        #logger.info(f"defaults: {defaults}")
        return defaults

    except Exception as e:
        logger.error(f"Errore durante l'aggregazione: {e}", exc_info=True)

# Helper functions per calcolare gli intervalli di date e i parametri corretti
def get_today():
    return timezone.now().date()

def get_week_params(today):
    start_of_week = today - timezone.timedelta(days=today.weekday())
    end_of_week = start_of_week + timezone.timedelta(days=6)
    return {'week': today.isocalendar()[1], 'year': today.year}, [start_of_week, end_of_week]

def get_month_params(today):
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)
    return {'month': today.month, 'year': today.year}, [start_of_month, end_of_month]

def get_quarter_params(today):
    quarter = (today.month - 1) // 3 + 1
    start_of_quarter = timezone.datetime(today.year, 3 * quarter - 2, 1).date()
    end_of_quarter = (timezone.datetime(today.year, 3 * quarter + 1, 1) - timezone.timedelta(days=1)).date()
    return {'quarter': quarter, 'year': today.year}, [start_of_quarter, end_of_quarter]

def get_year_params(today):
    start_of_year = today.replace(month=1, day=1)
    end_of_year = today.replace(month=12, day=31)
    return {'year': today.year}, [start_of_year, end_of_year]

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

