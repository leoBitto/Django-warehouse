# inventory/views/aggregated.py
from django.shortcuts import render
from datetime import datetime
from django.views import View
from inventory.models.aggregated import (
    InventoryGlobalAnnualAggregation, InventoryGlobalQuarterlyAggregation,
    ProductAnnualAggregation, ProductQuarterlyAggregation, ProductMonthlyAggregation,
    DataQualityQuarterlyAggregation, DataQualityAnnualAggregation,
    SalesDailyAggregation, SalesWeeklyAggregation, SalesMonthlyAggregation,
    SalesQuarterlyAggregation, SalesAnnualAggregation,
    OrdersDailyAggregation, OrdersWeeklyAggregation, OrdersMonthlyAggregation,
    OrdersQuarterlyAggregation, OrdersAnnualAggregation
)
from backoffice.forms import *
import logging
logger = logging.getLogger('app')
from django.db.models import Q


class GlobalReportView(View):
    pass


class ProductReportView(View):
    pass


class SalesReportView(View):
    pass


class OrdersReportView(View):
    pass


class DataQualityReportView(View):
    template_name = 'inventory/reports/select_aggregation.html'

    def get(self, request, *args, **kwargs):
        context = {
            'quarterly_form': QuarterlyAggregationForm(),
            'yearly_form': YearlyAggregationForm(),
            'report_type': 'Data Quality',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if 'quarterly_submit' in request.POST:
            form = QuarterlyAggregationForm(request.POST)
            aggregation_model = DataQualityQuarterlyAggregation
        elif 'yearly_submit' in request.POST:
            form = YearlyAggregationForm(request.POST)
            aggregation_model = DataQualityAnnualAggregation
        else:
            form = None
            aggregation_model = None

        if form and form.is_valid():
            if isinstance(form, QuarterlyAggregationForm):
                data = aggregation_model.objects.filter(
                    year=form.cleaned_data['year'],
                    quarter=form.cleaned_data['quarter']
                )
            elif isinstance(form, YearlyAggregationForm):
                data = aggregation_model.objects.filter(year=form.cleaned_data['year'])

            return render(request, 'inventory/reports/report.html', {
                'data': data,
                'report_type': 'Data Quality',
                'aggregation_type': form.cleaned_data.get('aggregation_type', 'Unknown')
            })

        context = {
            'quarterly_form': QuarterlyAggregationForm(),
            'yearly_form': YearlyAggregationForm(),
            'report_type': 'Data Quality',
        }
        return render(request, self.template_name, context)





def filter_data_by_aggregation_type(model, aggregation_type, start_date, end_date):
    if aggregation_type == 'daily':
        return model.objects.using('gold').filter(date__range=(start_date, end_date))
    
    elif aggregation_type == 'weekly':
        start_week = start_date.isocalendar()[1]
        end_week = end_date.isocalendar()[1]
        return model.objects.using('gold').filter(
            Q(year=start_date.year, week__gte=start_week) | 
            Q(year=end_date.year, week__lte=end_week)
        )
    
    elif aggregation_type == 'monthly':
        start_month = start_date.month
        end_month = end_date.month
        return model.objects.using('gold').filter(
            Q(year=start_date.year, month__gte=start_month) | 
            Q(year=end_date.year, month__lte=end_month)
        )
    
    elif aggregation_type == 'quarterly':
        start_quarter = (start_date.month - 1) // 3 + 1
        end_quarter = (end_date.month - 1) // 3 + 1
        return model.objects.using('gold').filter(
            Q(year=start_date.year, quarter__gte=start_quarter) | 
            Q(year=end_date.year, quarter__lte=end_quarter)
        )
    
    elif aggregation_type == 'yearly':
        return model.objects.using('gold').filter(year__range=(start_date.year, end_date.year))
    
    else:
        raise ValueError(f"Unknown aggregation type: {aggregation_type}")




def generate_report(request):
    # Ottieni i parametri dalla query string
    report_type = request.GET.get('report_type')
    aggregation_type = request.GET.get('aggregation_type')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Verifica se tutti i parametri necessari sono presenti
    if not all([report_type, aggregation_type, start_date_str, end_date_str]):
        return render(request, 'inventory/reports/report.html', {
            'error': 'Parametri mancanti. Assicurati di fornire tutti i parametri richiesti.'
        })

    # Conversione delle date da stringa a oggetto datetime
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return render(request, 'inventory/reports/report.html', {
            'error': 'Formato della data non valido.'
        })
    
    logger.info(f"report_type: {report_type}")
    logger.info(f"aggregation_type: {aggregation_type}")
    logger.info(f"start_date: {start_date}")
    logger.info(f"end_date: {end_date}")


    # Mappatura dei report_type e aggregation_type ai modelli corrispondenti
    model_map = {
        'global': {
            'yearly': InventoryGlobalAnnualAggregation,
            'quarterly': InventoryGlobalQuarterlyAggregation,
        },
        'product': {
            'yearly': ProductAnnualAggregation,
            'quarterly': ProductQuarterlyAggregation,
            'monthly': ProductMonthlyAggregation,
        },
        'data-quality': {
            'quarterly': DataQualityQuarterlyAggregation,
            'yearly': DataQualityAnnualAggregation,
        },
        'sales': {
            'daily': SalesDailyAggregation,
            'weekly': SalesWeeklyAggregation,
            'monthly': SalesMonthlyAggregation,
            'quarterly': SalesQuarterlyAggregation,
            'yearly': SalesAnnualAggregation,
        },
        'orders': {
            'daily': OrdersDailyAggregation,
            'weekly': OrdersWeeklyAggregation,
            'monthly': OrdersMonthlyAggregation,
            'quarterly': OrdersQuarterlyAggregation,
            'yearly': OrdersAnnualAggregation,
        }
    }

    # Selezione del modello corrispondente
    model = model_map.get(report_type, {}).get(aggregation_type)
    if not model:
        return render(request, 'inventory/reports/report.html', {
            'error': 'Tipo di report o aggregazione non valido.'
        })
    
    logger.info(f"model: {model}")

    # Query sui dati filtrati per date
    data = filter_data_by_aggregation_type(model, aggregation_type, start_date, end_date)    

    logger.info(f"data: {data}")

    # Passa i dati al template generico
    return render(request, 'inventory/reports/report.html', {
        'data': data,
        'report_type': report_type,
        'aggregation_type': aggregation_type,
        'start_date': start_date,
        'end_date': end_date,
    })
