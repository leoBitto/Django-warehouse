
from django.db import models
from gold_bi.models import DailyAggregationBase, WeeklyAggregationBase, MonthlyAggregationBase, QuarterlyAggregationBase, YearlyAggregationBase

class InventoryAggregationMixin(models.Model):
    """
    Modello astratto che aggiunge i campi specifici per l'aggregazione dell'inventario.
    """
    distinct_products_in_stock = models.IntegerField(null=True, blank=True)
    total_stock_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_sold_units = models.IntegerField(null=True, blank=True)
    total_sales_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_pending_sales = models.IntegerField(null=True, blank=True)
    total_delivered_sales = models.IntegerField(null=True, blank=True)
    total_paid_sales = models.IntegerField(null=True, blank=True)
    total_cancelled_sales = models.IntegerField(null=True, blank=True)
    total_ordered_units = models.IntegerField(null=True, blank=True)
    total_orders_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_pending_orders = models.IntegerField(null=True, blank=True)
    total_delivered_orders = models.IntegerField(null=True, blank=True)
    total_paid_orders = models.IntegerField(null=True, blank=True)
    total_cancelled_orders = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class InventoryDailyAggregation(InventoryAggregationMixin, DailyAggregationBase):
    class Meta:
        verbose_name = "Inventory Daily Aggregation"
        verbose_name_plural = "Inventory Daily Aggregations"


class InventoryWeeklyAggregation(InventoryAggregationMixin, WeeklyAggregationBase):
    class Meta:
        verbose_name = "Inventory Weekly Aggregation"
        verbose_name_plural = "Inventory Weekly Aggregations"


class InventoryMonthlyAggregation(InventoryAggregationMixin, MonthlyAggregationBase):
    class Meta:
        verbose_name = "Inventory Monthly Aggregation"
        verbose_name_plural = "Inventory Monthly Aggregations"


class InventoryQuarterlyAggregation(InventoryAggregationMixin, QuarterlyAggregationBase):
    class Meta:
        verbose_name = "Inventory Quarterly Aggregation"
        verbose_name_plural = "Inventory Quarterly Aggregations"


class InventoryYearlyAggregation(InventoryAggregationMixin, YearlyAggregationBase):
    class Meta:
        verbose_name = "Inventory Yearly Aggregation"
        verbose_name_plural = "Inventory Yearly Aggregations"


class InventoryQualityAggregation(MonthlyAggregationBase):
    """
    Modello per aggregare la qualità dei dati dei prodotti.
    """
    products_missing_category = models.IntegerField(null=True, blank=True)
    products_missing_image = models.IntegerField(null=True, blank=True)
    products_missing_description = models.IntegerField(null=True, blank=True)
    products_missing_both = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Inventory Quality Aggregation"
        verbose_name_plural = "Inventory Quality Aggregations"