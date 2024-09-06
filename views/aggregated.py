# inventory/views/aggregated.py
from django.shortcuts import render
from datetime import datetime, timedelta
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
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
logger = logging.getLogger('reports')

from backoffice.utils import *


class GlobalReportView(LoginRequiredMixin, View):
    template_name = 'backoffice/reports/select_aggregation.html'

    def get(self, request, *args, **kwargs):
        context = {
            'quarterly_form': QuarterlyAggregationForm(),
            'yearly_form': YearlyAggregationForm(),
            'report_type': 'Global',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = None
        aggregation_model = None
        period_type = None
        selected_period = None

        if 'quarterly_submit' in request.POST:
            form = QuarterlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = InventoryGlobalQuarterlyAggregation
                period_type = 'quarter'
                selected_period = {
                    'quarter': form.cleaned_data['quarter'],
                    'year': form.cleaned_data['year']
                }
        elif 'yearly_submit' in request.POST:
            form = YearlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = InventoryGlobalAnnualAggregation
                period_type = 'year'
                selected_period = {'year': form.cleaned_data['year']}

        if form and form.is_valid():
            # Ottieni i dati per i 6 periodi precedenti
            previous_periods_data = get_previous_periods(
                aggregation_model, selected_period, period_type, num_previous_periods=6
            )

            return render(request, 'inventory/reports/global_report.html', {
                'data': previous_periods_data,
                'report_type': 'Global',
                'period_type': period_type,
            })

        # Se il form non è valido o non è stato inviato, ricarica il form con gli errori
        context = {
            'quarterly_form': form if 'quarterly_submit' in request.POST else QuarterlyAggregationForm(),
            'yearly_form': form if 'yearly_submit' in request.POST else YearlyAggregationForm(),
            'report_type': 'Global',
        }
        return render(request, self.template_name, context)


class ProductReportView(LoginRequiredMixin, View):
    template_name = 'backoffice/reports/select_aggregation.html'

    def get(self, request, *args, **kwargs):
        context = {
            'monthly_form': MonthlyAggregationForm(),
            'quarterly_form': QuarterlyAggregationForm(),
            'yearly_form': YearlyAggregationForm(),
            'report_type': 'Product',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = None
        aggregation_model = None
        period_type = None
        selected_period = None

        if 'monthly_submit' in request.POST:
            form = MonthlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = ProductMonthlyAggregation
                period_type = 'month'
                selected_period = {
                    'month': form.cleaned_data['month'],
                    'year': form.cleaned_data['year']
                }
        elif 'quarterly_submit' in request.POST:
            form = QuarterlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = ProductQuarterlyAggregation
                period_type = 'quarter'
                selected_period = {
                    'quarter': form.cleaned_data['quarter'],
                    'year': form.cleaned_data['year']
                }
        elif 'yearly_submit' in request.POST:
            form = YearlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = ProductAnnualAggregation
                period_type = 'year'
                selected_period = {'year': form.cleaned_data['year']}

        if form and form.is_valid():
            previous_periods_data = get_previous_periods(
                aggregation_model, selected_period, period_type, num_previous_periods=6
            )
            return render(request, 'inventory/reports/product_report.html', {
                'data': previous_periods_data,
                'report_type': 'Product',
                'period_type': period_type,
            })

        context = {
            'monthly_form': form if 'monthly_submit' in request.POST else MonthlyAggregationForm(),
            'quarterly_form': form if 'quarterly_submit' in request.POST else QuarterlyAggregationForm(),
            'yearly_form': form if 'yearly_submit' in request.POST else YearlyAggregationForm(),
            'report_type': 'Product',
        }
        return render(request, self.template_name, context)


class SalesReportView(LoginRequiredMixin, View):
    template_name = 'backoffice/reports/select_aggregation.html'

    def get(self, request, *args, **kwargs):
        context = {
            'daily_form': DailyAggregationForm(),
            'weekly_form': WeeklyAggregationForm(),
            'monthly_form': MonthlyAggregationForm(),
            'quarterly_form': QuarterlyAggregationForm(),
            'yearly_form': YearlyAggregationForm(),
            'report_type': 'Sales',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = None
        aggregation_model = None
        period_type = None
        selected_period = None

        if 'daily_submit' in request.POST:
            form = DailyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = SalesDailyAggregation
                period_type = 'day'
                selected_period = form.cleaned_data['date']
        elif 'weekly_submit' in request.POST:
            form = WeeklyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = SalesWeeklyAggregation
                period_type = 'week'
                selected_period = {
                    'week': form.cleaned_data['week'],
                    'year': form.cleaned_data['year']
                }
        elif 'monthly_submit' in request.POST:
            form = MonthlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = SalesMonthlyAggregation
                period_type = 'month'
                selected_period = {
                    'month': form.cleaned_data['month'],
                    'year': form.cleaned_data['year']
                }
        elif 'quarterly_submit' in request.POST:
            form = QuarterlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = SalesQuarterlyAggregation
                period_type = 'quarter'
                selected_period = {
                    'quarter': form.cleaned_data['quarter'],
                    'year': form.cleaned_data['year']
                }
        elif 'yearly_submit' in request.POST:
            form = YearlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = SalesAnnualAggregation
                period_type = 'year'
                selected_period = {'year': form.cleaned_data['year']}

        if form and form.is_valid():
            previous_periods_data = get_previous_periods(
                aggregation_model, selected_period, period_type, num_previous_periods=6
            )
            for data in previous_periods_data:
                logger.info(f"{data}")


            return render(request, 'inventory/reports/sales_report.html', {
                'data': previous_periods_data,
                'report_type': 'Sales',
                'period_type': period_type,
            })

        context = {
            'daily_form': form if 'daily_submit' in request.POST else DailyAggregationForm(),
            'weekly_form': form if 'weekly_submit' in request.POST else WeeklyAggregationForm(),
            'monthly_form': form if 'monthly_submit' in request.POST else MonthlyAggregationForm(),
            'quarterly_form': form if 'quarterly_submit' in request.POST else QuarterlyAggregationForm(),
            'yearly_form': form if 'yearly_submit' in request.POST else YearlyAggregationForm(),
            'report_type': 'Sales',
        }
        return render(request, self.template_name, context)


class OrdersReportView(LoginRequiredMixin, View):
    template_name = 'backoffice/reports/select_aggregation.html'

    def get(self, request, *args, **kwargs):
        context = {
            'daily_form': DailyAggregationForm(),
            'weekly_form': WeeklyAggregationForm(),
            'monthly_form': MonthlyAggregationForm(),
            'quarterly_form': QuarterlyAggregationForm(),
            'yearly_form': YearlyAggregationForm(),
            'report_type': 'Orders',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = None
        aggregation_model = None
        period_type = None
        selected_period = None

        if 'daily_submit' in request.POST:
            form = DailyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = OrdersDailyAggregation
                period_type = 'day'
                selected_period = form.cleaned_data['date']
        elif 'weekly_submit' in request.POST:
            form = WeeklyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = OrdersWeeklyAggregation
                period_type = 'week'
                selected_period = {
                    'week': form.cleaned_data['week'],
                    'year': form.cleaned_data['year']
                }
        elif 'monthly_submit' in request.POST:
            form = MonthlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = OrdersMonthlyAggregation
                period_type = 'month'
                selected_period = {
                    'month': form.cleaned_data['month'],
                    'year': form.cleaned_data['year']
                }
        elif 'quarterly_submit' in request.POST:
            form = QuarterlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = OrdersQuarterlyAggregation
                period_type = 'quarter'
                selected_period = {
                    'quarter': form.cleaned_data['quarter'],
                    'year': form.cleaned_data['year']
                }
        elif 'yearly_submit' in request.POST:
            form = YearlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = OrdersAnnualAggregation
                period_type = 'year'
                selected_period = {'year': form.cleaned_data['year']}

        if form and form.is_valid():
            previous_periods_data = get_previous_periods(
                aggregation_model, selected_period, period_type, num_previous_periods=6
            )
            #logger.info(f"data: {previous_periods_data}")

            return render(request, 'inventory/reports/orders_report.html', {
                'data': previous_periods_data,
                'report_type': 'Orders',
                'period_type': period_type,
            })

        context = {
            'daily_form': form if 'daily_submit' in request.POST else DailyAggregationForm(),
            'weekly_form': form if 'weekly_submit' in request.POST else WeeklyAggregationForm(),
            'monthly_form': form if 'monthly_submit' in request.POST else MonthlyAggregationForm(),
            'quarterly_form': form if 'quarterly_submit' in request.POST else QuarterlyAggregationForm(),
            'yearly_form': form if 'yearly_submit' in request.POST else YearlyAggregationForm(),
            'report_type': 'Orders',
        }
        return render(request, self.template_name, context)


class DataQualityReportView(LoginRequiredMixin, View):
    template_name = 'backoffice/reports/select_aggregation.html'

    def get(self, request, *args, **kwargs):
        context = {
            'quarterly_form': QuarterlyAggregationForm(),
            'yearly_form': YearlyAggregationForm(),
            'report_type': 'Data Quality',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = None
        aggregation_model = None
        period_type = None
        selected_period = None

        if 'quarterly_submit' in request.POST:
            form = QuarterlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = DataQualityQuarterlyAggregation
                period_type = 'quarter'
                selected_period = {
                    'quarter': form.cleaned_data['quarter'],
                    'year': form.cleaned_data['year']
                }
        elif 'yearly_submit' in request.POST:
            form = YearlyAggregationForm(request.POST)
            if form.is_valid():
                aggregation_model = DataQualityAnnualAggregation
                period_type = 'year'
                selected_period = {'year': form.cleaned_data['year']}

        if form and form.is_valid():
            # Ottieni i dati per i 6 periodi precedenti
            previous_periods_data = get_previous_periods(
                aggregation_model, selected_period, period_type, num_previous_periods=6
            )

            return render(request, 'inventory/reports/quality_report.html', {
                'data': previous_periods_data,
                'report_type': 'Data Quality',
                'period_type': period_type,
            })

        context = {
            'quarterly_form': form if 'quarterly_submit' in request.POST else QuarterlyAggregationForm(),
            'yearly_form': form if 'yearly_submit' in request.POST else YearlyAggregationForm(),
            'report_type': 'Data Quality',
        }
        return render(request, self.template_name, context)


