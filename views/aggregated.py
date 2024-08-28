from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models.aggregated import (
    InventoryDailyAggregation, InventoryWeeklyAggregation,
    InventoryMonthlyAggregation, InventoryQuarterlyAggregation,
    InventoryYearlyAggregation
)
import plotly.graph_objs as go
from plotly.offline import plot

class GenerateReportView(LoginRequiredMixin, View):
    """
    Vista per generare report basati su dati di aggregazione dell'inventario.
    Gestisce la visualizzazione dei dati e la generazione di grafici.
    """
    template_name = 'inventory/reports/inventory_report.html'

    # Mappa per selezionare il modello corretto in base al tipo di report
    model_map = {
        'daily': InventoryDailyAggregation,
        'weekly': InventoryWeeklyAggregation,
        'monthly': InventoryMonthlyAggregation,
        'quarterly': InventoryQuarterlyAggregation,
        'yearly': InventoryYearlyAggregation,
    }

    def get_queryset(self, report_type, start_date, end_date):
        """
        Recupera il queryset dei dati basato sul tipo di report e sull'intervallo di date.

        :param report_type: Tipo di report ('daily', 'weekly', etc.)
        :param start_date: Data di inizio dell'intervallo
        :param end_date: Data di fine dell'intervallo
        :return: QuerySet dei dati filtrati
        """
        model = self.model_map.get(report_type)
        if model:
            return model.objects.using('gold').filter(date__range=[start_date, end_date]).order_by('-date')
        return model.objects.none()

    def generate_graph(self, data, report_type, x_data_key='date', y_data_key='total_sales_value', graph_type='lines+markers', title=None, xaxis_title='Date', yaxis_title='Value'):
        """
        Genera un grafico utilizzando Plotly basato sui dati forniti.

        :param data: Lista di oggetti o dizionari contenenti i dati da visualizzare
        :param report_type: Tipo di report per il titolo e la legenda
        :param x_data_key: Chiave per i dati sull'asse X
        :param y_data_key: Chiave per i dati sull'asse Y
        :param graph_type: Tipo di grafico (es. 'lines+markers', 'bars', etc.)
        :param title: Titolo del grafico
        :param xaxis_title: Titolo dell'asse X
        :param yaxis_title: Titolo dell'asse Y
        :return: Div HTML del grafico
        """
        x_data = [getattr(item, x_data_key) for item in data]
        y_data = [getattr(item, y_data_key) for item in data]

        trace = go.Scatter(
            x=x_data,
            y=y_data,
            mode=graph_type,
            name=f'{report_type.capitalize()} Data'
        )

        layout = go.Layout(
            title=title or f'{report_type.capitalize()} Data Report',
            xaxis=dict(title=xaxis_title),
            yaxis=dict(title=yaxis_title),
            template='plotly_dark'
        )

        fig = go.Figure(data=[trace], layout=layout)
        graph_div = plot(fig, output_type='div')
        return graph_div

    def get(self, request, *args, **kwargs):
        """
        Gestisce la richiesta GET per generare e visualizzare il report.

        :param request: Oggetto HttpRequest
        :return: Risposta HttpResponse con il contesto del report e i grafici
        """
        report_type = request.GET.get('report_type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Recupera i dati
        report_data = self.get_queryset(report_type, start_date, end_date)

        # Genera i grafici
        graph_sales = self.generate_graph(
            report_data,
            report_type,
            x_data_key='date',
            y_data_key='total_sales_value',
            graph_type='lines+markers',
            title='Total Sales Value',
            xaxis_title='Date',
            yaxis_title='Total Sales Value'
        )
        
        graph_stock_value = self.generate_graph(
            report_data,
            report_type,
            x_data_key='date',
            y_data_key='total_stock_value',
            graph_type='lines+markers',
            title='Total Stock Value',
            xaxis_title='Date',
            yaxis_title='Total Stock Value'
        )

        context = {
            'report_type': report_type,
            'start_date': start_date,
            'end_date': end_date,
            'report_data': report_data,
            'graph_sales': graph_sales,
            'graph_stock_value': graph_stock_value
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Gestisce la richiesta POST, se necessario.

        :param request: Oggetto HttpRequest
        :return: Risposta HttpResponse
        """
        # Implementa la logica per le richieste POST se necessario
        pass
