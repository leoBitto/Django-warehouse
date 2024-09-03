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
    def __str__(self):
        return f"Year: {self.year}"

class InventoryGlobalQuarterlyAggregation(InventoryGlobalAggregationMixin, QuarterlyAggregationBase):
    def __str__(self):
        return f"Year: {self.year}, Quarter: {self.quarter}"


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

    def __str__(self):
        return f"Year: {self.year}, Product: {self.product.name}"

class ProductQuarterlyAggregation(ProductAggregationMixin, QuarterlyAggregationBase):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='quarterly_aggregations')

    def __str__(self):
        return f"Year: {self.year}, Quarter: {self.quarter}, Product: {self.product.name}"

class ProductMonthlyAggregation(ProductAggregationMixin, MonthlyAggregationBase):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='monthly_aggregations')

    def __str__(self):
        return f"Year: {self.year}, Month: {self.month}, Product: {self.product.name}"


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
    def __str__(self):
        return f"Year: {self.year}, Quarter: {self.quarter}"

class DataQualityAnnualAggregation(DataQualityAggregationMixin, YearlyAggregationBase):
    def __str__(self):
        return f"Year: {self.year}"


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
    sold_products_count_by_category = models.JSONField(null=True, blank=True)
    gross_margin = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    average_sales_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    class Meta:
        abstract = True

class SalesDailyAggregation(SalesAggregationMixin, DailyAggregationBase):
    def __str__(self):
        return f"Date: {self.date}"

class SalesWeeklyAggregation(SalesAggregationMixin, WeeklyAggregationBase):
    def __str__(self):
        return f"Year: {self.year}, Week: {self.week}"

class SalesMonthlyAggregation(SalesAggregationMixin, MonthlyAggregationBase):
    def __str__(self):
        return f"Year: {self.year}, Month: {self.month}"

class SalesQuarterlyAggregation(SalesAggregationMixin, QuarterlyAggregationBase):
    def __str__(self):
        return f"Year: {self.year}, Quarter: {self.quarter}"

class SalesAnnualAggregation(SalesAggregationMixin, YearlyAggregationBase):
    def __str__(self):
        return f"Year: {self.year}"


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
    ordered_products_count_by_category = models.JSONField(null=True, blank=True)
    gross_margin = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    average_order_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    growth_rate_previous_period = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    growth_rate_same_period_last_year = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        abstract = True

class OrdersDailyAggregation(OrdersAggregationMixin, DailyAggregationBase):
    def __str__(self):
        return f"Date: {self.date}"

class OrdersWeeklyAggregation(OrdersAggregationMixin, WeeklyAggregationBase):
    def __str__(self):
        return f"Year: {self.year}, Week: {self.week}"

class OrdersMonthlyAggregation(OrdersAggregationMixin, MonthlyAggregationBase):
    def __str__(self):
        return f"Year: {self.year}, Month: {self.month}"

class OrdersQuarterlyAggregation(OrdersAggregationMixin, QuarterlyAggregationBase):
    def __str__(self):
        return f"Year: {self.year}, Quarter: {self.quarter}"

class OrdersAnnualAggregation(OrdersAggregationMixin, YearlyAggregationBase):
    def __str__(self):
        return f"Year: {self.year}"
