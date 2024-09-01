from django.db import models
from inventory.models.base import *
from gold_bi.models import (
    DailyAggregationBase,
    WeeklyAggregationBase,
    MonthlyAggregationBase,
    QuarterlyAggregationBase,
    YearlyAggregationBase
)

class InventoryGlobalAggregationMixin(models.Model):
    distinct_products_count = models.IntegerField(null=True, blank=True)
    products_count_by_category = models.JSONField(null=True, blank=True)
    total_products_count = models.IntegerField(null=True, blank=True)
    total_inventory_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    inventory_value_by_category = models.JSONField(null=True, blank=True)

    class Meta:
        abstract = True

class InventoryGlobalAnnualAggregation(InventoryGlobalAggregationMixin, YearlyAggregationBase):
    pass

class InventoryGlobalQuarterlyAggregation(InventoryGlobalAggregationMixin, QuarterlyAggregationBase):
    pass


class ProductAggregationMixin(models.Model):
    product_quantity = models.IntegerField(null=True, blank=True)
    total_product_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    gross_margin = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    suppliers_count = models.IntegerField(null=True, blank=True)
    customers_count = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True

class ProductAnnualAggregation(ProductAggregationMixin, YearlyAggregationBase):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='annual_aggregations')

class ProductQuarterlyAggregation(ProductAggregationMixin, QuarterlyAggregationBase):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='quarterly_aggregations')

class ProductMonthlyAggregation(ProductAggregationMixin, MonthlyAggregationBase):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='monthly_aggregations')


# Aggregazioni della Qualità dei Dati
class DataQualityAggregationMixin(models.Model):
    products_missing_image_count = models.IntegerField(null=True, blank=True)
    products_missing_description_count = models.IntegerField(null=True, blank=True)
    products_missing_both_count = models.IntegerField(null=True, blank=True)
    products_missing_category_count = models.IntegerField(null=True, blank=True)
    sales_missing_customer_count = models.IntegerField(null=True, blank=True)
    orders_missing_supplier_code_count = models.IntegerField(null=True, blank=True)
    orders_missing_supplier_count = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True

class DataQualityQuarterlyAggregation(DataQualityAggregationMixin, QuarterlyAggregationBase):
    pass

class DataQualityAnnualAggregation(DataQualityAggregationMixin, YearlyAggregationBase):
    pass


class SalesAggregationMixin(models.Model):
    total_sales_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    sales_pending_count = models.IntegerField(null=True, blank=True)
    sales_sold_count = models.IntegerField(null=True, blank=True)
    sales_delivered_count = models.IntegerField(null=True, blank=True)
    sales_paid_count = models.IntegerField(null=True, blank=True)
    sales_cancelled_count = models.IntegerField(null=True, blank=True)
    
    days_between_sale_and_delivery = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    days_between_sale_and_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    customers_count = models.IntegerField(null=True, blank=True)
    sold_products_count = models.IntegerField(null=True, blank=True)
    sold_products_count_by_category = models.JSONField(null=True, blank=True)  # Puoi espandere questa struttura con campi specifici per categoria
    gross_margin = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    average_sales_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    class Meta:
        abstract = True

class SalesDailyAggregation(SalesAggregationMixin, DailyAggregationBase):
    pass

class SalesWeeklyAggregation(SalesAggregationMixin, WeeklyAggregationBase):
    pass

class SalesMonthlyAggregation(SalesAggregationMixin, MonthlyAggregationBase):
    pass

class SalesQuarterlyAggregation(SalesAggregationMixin, QuarterlyAggregationBase):
    pass

class SalesAnnualAggregation(SalesAggregationMixin, YearlyAggregationBase):
    pass


class OrdersAggregationMixin(models.Model):
    total_orders_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    orders_pending_count = models.IntegerField(null=True, blank=True)
    orders_sold_count = models.IntegerField(null=True, blank=True)
    orders_delivered_count = models.IntegerField(null=True, blank=True)
    orders_paid_count = models.IntegerField(null=True, blank=True)
    orders_cancelled_count = models.IntegerField(null=True, blank=True)
    
    days_between_order_and_delivery = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    days_between_order_and_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    suppliers_count = models.IntegerField(null=True, blank=True)
    ordered_products_count = models.IntegerField(null=True, blank=True)
    ordered_products_count_by_category = models.JSONField(null=True, blank=True)  # Puoi espandere questa struttura con campi specifici per categoria
    gross_margin = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    average_order_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    growth_rate_previous_period = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    growth_rate_same_period_last_year = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        abstract = True

class OrdersDailyAggregation(OrdersAggregationMixin, DailyAggregationBase):
    pass

class OrdersWeeklyAggregation(OrdersAggregationMixin, WeeklyAggregationBase):
    pass

class OrdersMonthlyAggregation(OrdersAggregationMixin, MonthlyAggregationBase):
    pass

class OrdersQuarterlyAggregation(OrdersAggregationMixin, QuarterlyAggregationBase):
    pass

class OrdersAnnualAggregation(OrdersAggregationMixin, YearlyAggregationBase):
    pass
