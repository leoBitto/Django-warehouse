from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models.aggregated import (
    InventoryDailyAggregation, InventoryWeeklyAggregation,
    InventoryMonthlyAggregation, InventoryQuarterlyAggregation,
    InventoryYearlyAggregation
)
import plotly.graph_objs as go
from plotly.offline import plot

class GenerateReportView(LoginRequiredMixin, ListView):
    template_name = 'inventory/reports/view_inventory_report.html'
    context_object_name = 'aggregations'

    # Mappa per selezionare il modello corretto in base al tipo di report
    model_map = {
        'daily': InventoryDailyAggregation,
        'weekly': InventoryWeeklyAggregation,
        'monthly': InventoryMonthlyAggregation,
        'quarterly': InventoryQuarterlyAggregation,
        'yearly': InventoryYearlyAggregation,
    }

    def get_queryset(self):
        report_type = self.request.GET.get('report_type')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        # Seleziona il modello corretto
        model = self.model_map.get(report_type)
        if model:
            # Filtra i dati in base all'intervallo temporale
            return model.objects.using('gold').filter(date__range=[start_date, end_date]).order_by('-date')
        return model.objects.none()

    def generate_graph(self, aggregations, report_type):
        # Esempio: Grafico a linee per il valore totale delle vendite
        dates = [agg.date for agg in aggregations]
        values = [agg.total_sales_value for agg in aggregations]

        trace = go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name=f'{report_type.capitalize()} Sales'
        )

        layout = go.Layout(
            title=f'{report_type.capitalize()} Sales Report',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Total Sales Value'),
            template='plotly_dark'
        )

        fig = go.Figure(data=[trace], layout=layout)

        # Genera l'HTML del grafico
        graph_div = plot(fig, output_type='div')
        return graph_div

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report_type = self.request.GET.get('report_type')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        # Aggiunge informazioni extra al contesto
        context['report_type'] = report_type
        context['start_date'] = start_date
        context['end_date'] = end_date

        # Genera il grafico e lo aggiunge al contesto
        aggregations = context['aggregations']
        context['graph'] = self.generate_graph(aggregations, report_type)

        return context
