from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models.aggregated import InventoryDailyAggregation, InventoryWeeklyAggregation, InventoryMonthlyAggregation, InventoryQuarterlyAggregation, InventoryYearlyAggregation

class ReportView(LoginRequiredMixin, ListView):
    template_name = 'inventory/reports/view_inventory_report.html'
    context_object_name = 'aggregations'

    def get_queryset(self):
        report_type = self.request.GET.get('report_type')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        model_map = {
            'daily': InventoryDailyAggregation,
            'weekly': InventoryWeeklyAggregation,
            'monthly': InventoryMonthlyAggregation,
            'quarterly': InventoryQuarterlyAggregation,
            'yearly': InventoryYearlyAggregation,
        }

        model = model_map.get(report_type)
        if model:
            return model.objects.filter(date__range=[start_date, end_date]).order_by('-date')
        return model.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_type'] = self.request.GET.get('report_type')
        context['start_date'] = self.request.GET.get('start_date')
        context['end_date'] = self.request.GET.get('end_date')
        return context
