import logging
from django.utils import timezone
from django.db import transaction
from django.db.models import Avg, Count, Sum, F
from inventory.models.base import Sale
from inventory.models.aggregated import (
    SalesDailyAggregation, SalesWeeklyAggregation, SalesMonthlyAggregation, 
    SalesQuarterlyAggregation, SalesAnnualAggregation
)


logger = logging.getLogger('app')

def aggregate_sales_daily():
    try:
        today = timezone.now().date()

        sales = Sale.objects.filter(sale_date__range=[today, today])

        # Aggregazione delle metriche
        total_sales_value = 0
        sales_pending_count = sales.filter(status='pending').count()
        sales_sold_count = sales.filter(status='sold').count()
        sales_delivered_count = sales.filter(status='delivered').count()
        sales_paid_count = sales.filter(status='paid').count()
        sales_cancelled_count = sales.filter(status='cancelled').count()


        # Calcolo della media dei giorni tra la data di vendita e la data di consegna
        days_between_sale_and_delivery = sales.exclude(delivery_date__isnull=True).aggregate(
            Avg(F('delivery_date') - F('sale_date'))
        )['delivery_date__sale_date__avg'].days or 0

        # Calcolo della media dei giorni tra la data di vendita e la data di pagamento
        days_between_sale_and_payment = sales.exclude(payment_date__isnull=True).aggregate(
            Avg(F('payment_date') - F('sale_date'))
        )['payment_date__sale_date__avg'].days or 0

        # Conta dei clienti unici che hanno effettuato acquisti
        customers_count = sales.aggregate(Count('customer', distinct=True))['customer__count'] or 0

        # Totale dei prodotti venduti
        sold_products_count = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0

        # Conta dei prodotti venduti per categoria
        sold_products_count_by_category = sales.values('product__category').annotate(
            total_sold=Sum('quantity')
        )

        # Calcolo del margine lordo totale (ricavo - costo dei beni venduti)
        gross_margin = sales.aggregate(
            gross_margin=Sum(F('total_price') - F('quantity') * F('product__cost'))
        )['gross_margin'] or 0

        # Calcolo del valore medio delle vendite
        average_sales_value = total_sales_value / sales_sold_count if sales_sold_count else 0



        with transaction.atomic():
            SalesDailyAggregation.objects.using('gold').update_or_create(
                date=today,
                defaults={
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
                    'sold_products_count_by_category': sold_products_count_by_category,
                    'gross_margin': gross_margin,
                    'average_sales_value': average_sales_value,
                    
                }
            )

        logger.info(f'Aggregazione giornaliera delle vendite completata per il giorno {today}.')

    except Exception as e:
            logger.error(f'Errore durante l\'aggregazione giornaliera delle vendite per il giorno {today}: {e}')

def aggregate_sales_weekly():
    try:
        today = timezone.now().date()
        start_of_week = today - timezone.timedelta(days=today.weekday())
        end_of_week = start_of_week + timezone.timedelta(days=6)

        # Recupero delle vendite della settimana corrente
        sales = Sale.objects.filter(sale_date__range=[start_of_week, end_of_week])

        # Aggregazione delle metriche
        total_sales_value = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
        sales_pending_count = sales.filter(status='pending').count()
        sales_sold_count = sales.filter(status='sold').count()
        sales_delivered_count = sales.filter(status='delivered').count()
        sales_paid_count = sales.filter(status='paid').count()
        sales_cancelled_count = sales.filter(status='cancelled').count()

        days_between_sale_and_delivery = sales.exclude(delivery_date__isnull=True).aggregate(
            Avg(F('delivery_date') - F('sale_date'))
        )['delivery_date__sale_date__avg'].days or 0

        days_between_sale_and_payment = sales.exclude(payment_date__isnull=True).aggregate(
            Avg(F('payment_date') - F('sale_date'))
        )['payment_date__sale_date__avg'].days or 0

        customers_count = sales.aggregate(Count('customer', distinct=True))['customer__count'] or 0
        sold_products_count = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0

        sold_products_count_by_category = sales.values('product__category').annotate(
            total_sold=Sum('quantity')
        )

        gross_margin = sales.aggregate(
            gross_margin=Sum(F('total_price') - F('quantity') * F('product__cost'))
        )['gross_margin'] or 0

        average_sales_value = total_sales_value / sales_sold_count if sales_sold_count else 0

        with transaction.atomic():
            SalesWeeklyAggregation.objects.using('gold').update_or_create(
                start_date=start_of_week,
                defaults={
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
                    'sold_products_count_by_category': sold_products_count_by_category,
                    'gross_margin': gross_margin,
                    'average_sales_value': average_sales_value,
                }
            )

        logger.info(f'Aggregazione settimanale delle vendite completata per la settimana {start_of_week} - {end_of_week}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione settimanale delle vendite per la settimana {start_of_week} - {end_of_week}: {e}')

def aggregate_sales_monthly():
    try:
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)

        # Recupero delle vendite del mese corrente
        sales = Sale.objects.filter(sale_date__range=[start_of_month, end_of_month])

        # Aggregazione delle metriche
        total_sales_value = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
        sales_pending_count = sales.filter(status='pending').count()
        sales_sold_count = sales.filter(status='sold').count()
        sales_delivered_count = sales.filter(status='delivered').count()
        sales_paid_count = sales.filter(status='paid').count()
        sales_cancelled_count = sales.filter(status='cancelled').count()

        days_between_sale_and_delivery = sales.exclude(delivery_date__isnull=True).aggregate(
            Avg(F('delivery_date') - F('sale_date'))
        )['delivery_date__sale_date__avg'].days or 0

        days_between_sale_and_payment = sales.exclude(payment_date__isnull=True).aggregate(
            Avg(F('payment_date') - F('sale_date'))
        )['payment_date__sale_date__avg'].days or 0

        customers_count = sales.aggregate(Count('customer', distinct=True))['customer__count'] or 0
        sold_products_count = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0

        sold_products_count_by_category = sales.values('product__category').annotate(
            total_sold=Sum('quantity')
        )

        gross_margin = sales.aggregate(
            gross_margin=Sum(F('total_price') - F('quantity') * F('product__cost'))
        )['gross_margin'] or 0

        average_sales_value = total_sales_value / sales_sold_count if sales_sold_count else 0

        with transaction.atomic():
            SalesMonthlyAggregation.objects.using('gold').update_or_create(
                start_date=start_of_month,
                defaults={
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
                    'sold_products_count_by_category': sold_products_count_by_category,
                    'gross_margin': gross_margin,
                    'average_sales_value': average_sales_value,
                }
            )

        logger.info(f'Aggregazione mensile delle vendite completata per il mese {start_of_month}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione mensile delle vendite per il mese {start_of_month}: {e}')

def aggregate_sales_quarterly():
    try:
        today = timezone.now().date()
        quarter = (today.month - 1) // 3 + 1
        start_of_quarter = timezone.datetime(today.year, 3 * quarter - 2, 1).date()
        end_of_quarter = (timezone.datetime(today.year, 3 * quarter + 1, 1) - timezone.timedelta(days=1)).date()

        # Recupero delle vendite del trimestre corrente
        sales = Sale.objects.filter(sale_date__range=[start_of_quarter, end_of_quarter])

        # Aggregazione delle metriche
        total_sales_value = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
        sales_pending_count = sales.filter(status='pending').count()
        sales_sold_count = sales.filter(status='sold').count()
        sales_delivered_count = sales.filter(status='delivered').count()
        sales_paid_count = sales.filter(status='paid').count()
        sales_cancelled_count = sales.filter(status='cancelled').count()

        days_between_sale_and_delivery = sales.exclude(delivery_date__isnull=True).aggregate(
            Avg(F('delivery_date') - F('sale_date'))
        )['delivery_date__sale_date__avg'].days or 0

        days_between_sale_and_payment = sales.exclude(payment_date__isnull=True).aggregate(
            Avg(F('payment_date') - F('sale_date'))
        )['payment_date__sale_date__avg'].days or 0

        customers_count = sales.aggregate(Count('customer', distinct=True))['customer__count'] or 0
        sold_products_count = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0

        sold_products_count_by_category = sales.values('product__category').annotate(
            total_sold=Sum('quantity')
        )

        gross_margin = sales.aggregate(
            gross_margin=Sum(F('total_price') - F('quantity') * F('product__cost'))
        )['gross_margin'] or 0

        average_sales_value = total_sales_value / sales_sold_count if sales_sold_count else 0

        with transaction.atomic():
            SalesQuarterlyAggregation.objects.using('gold').update_or_create(
                start_date=start_of_quarter,
                defaults={
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
                    'sold_products_count_by_category': sold_products_count_by_category,
                    'gross_margin': gross_margin,
                    'average_sales_value': average_sales_value,
                }
            )

        logger.info(f'Aggregazione trimestrale delle vendite completata per il trimestre {quarter}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione trimestrale delle vendite per il trimestre {quarter}: {e}')

def aggregate_sales_annually():
    try:
        today = timezone.now().date()
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)

        # Recupero delle vendite dell'anno corrente
        sales = Sale.objects.filter(sale_date__range=[start_of_year, end_of_year])

        # Aggregazione delle metriche
        total_sales_value = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
        sales_pending_count = sales.filter(status='pending').count()
        sales_sold_count = sales.filter(status='sold').count()
        sales_delivered_count = sales.filter(status='delivered').count()
        sales_paid_count = sales.filter(status='paid').count()
        sales_cancelled_count = sales.filter(status='cancelled').count()

        days_between_sale_and_delivery = sales.exclude(delivery_date__isnull=True).aggregate(
            Avg(F('delivery_date') - F('sale_date'))
        )['delivery_date__sale_date__avg'].days or 0

        days_between_sale_and_payment = sales.exclude(payment_date__isnull=True).aggregate(
            Avg(F('payment_date') - F('sale_date'))
        )['payment_date__sale_date__avg'].days or 0

        customers_count = sales.aggregate(Count('customer', distinct=True))['customer__count'] or 0
        sold_products_count = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0

        sold_products_count_by_category = sales.values('product__category').annotate(
            total_sold=Sum('quantity')
        )

        gross_margin = sales.aggregate(
            gross_margin=Sum(F('total_price') - F('quantity') * F('product__cost'))
        )['gross_margin'] or 0

        average_sales_value = total_sales_value / sales_sold_count if sales_sold_count else 0

        with transaction.atomic():
            SalesAnnualAggregation.objects.using('gold').update_or_create(
                start_date=start_of_year,
                defaults={
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
                    'sold_products_count_by_category': sold_products_count_by_category,
                    'gross_margin': gross_margin,
                    'average_sales_value': average_sales_value,
                }
            )

        logger.info(f'Aggregazione annuale delle vendite completata per l\'anno {start_of_year.year}.')

    except Exception as e:
        logger.error(f'Errore durante l\'aggregazione annuale delle vendite per l\'anno {start_of_year.year}: {e}')
