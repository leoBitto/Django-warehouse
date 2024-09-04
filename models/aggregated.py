from django.db import models
from django.utils.translation import gettext_lazy as _
from inventory.models.base import *
from gold_bi.models import (
    DailyAggregationBase,
    WeeklyAggregationBase,
    MonthlyAggregationBase,
    QuarterlyAggregationBase,
    YearlyAggregationBase
)

class InventoryGlobalAggregationMixin(models.Model):
    distinct_products_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Prodotti Distinti"))
    products_count_by_category = models.JSONField(null=True, blank=True, verbose_name=_("Conteggio Prodotti per Categoria"))
    total_products_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Totale Prodotti"))
    total_inventory_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Valore Totale Inventario"))
    inventory_value_by_category = models.JSONField(null=True, blank=True, verbose_name=_("Valore Inventario per Categoria"))

    class Meta:
        abstract = True

class InventoryGlobalAnnualAggregation(InventoryGlobalAggregationMixin, YearlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}"

class InventoryGlobalQuarterlyAggregation(InventoryGlobalAggregationMixin, QuarterlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}, Trimestre: {self.quarter}"


class ProductAggregationMixin(models.Model):
    product_name = models.CharField(_("Nome Prodotto"), max_length=200)
    product_internal_code = models.CharField(_("Codice Interno Prodotto"), max_length=50, null=True, blank=True)
    product_quantity = models.IntegerField(null=True, blank=True, verbose_name=_("Quantità Prodotto"))
    total_product_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Valore Totale Prodotto"))
    gross_margin = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Margine Lordo"))
    suppliers_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Fornitori"))
    customers_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Clienti"))

    class Meta:
        abstract = True

class ProductAnnualAggregation(ProductAggregationMixin, YearlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}, Prodotto: {self.product_name}"

class ProductQuarterlyAggregation(ProductAggregationMixin, QuarterlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}, Trimestre: {self.quarter}, Prodotto: {self.product_name}"

class ProductMonthlyAggregation(ProductAggregationMixin, MonthlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}, Mese: {self.month}, Prodotto: {self.product_name}"


class DataQualityAggregationMixin(models.Model):
    products_missing_image_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Prodotti Senza Immagine"))
    products_missing_description_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Prodotti Senza Descrizione"))
    products_missing_both_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Prodotti Senza immagine né descrizione"))
    products_missing_category_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Prodotti Senza Categoria"))
    sales_missing_customer_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Vendite Senza Cliente"))
    orders_missing_supplier_code_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Ordini Senza Codice Fornitore"))
    orders_missing_supplier_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Ordini Senza Fornitore"))

    class Meta:
        abstract = True

class DataQualityQuarterlyAggregation(DataQualityAggregationMixin, QuarterlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}, Trimestre: {self.quarter}"

class DataQualityAnnualAggregation(DataQualityAggregationMixin, YearlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}"


class SalesAggregationMixin(models.Model):
    total_sales_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Valore Totale Vendite"))
    sales_pending_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Vendite Pendenti"))
    sales_sold_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Vendite Vendute"))
    sales_delivered_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Vendite Consegnate"))
    sales_paid_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Vendite Pagate"))
    sales_cancelled_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Vendite Cancellate"))
    
    days_between_sale_and_delivery = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Giorni tra Vendita e Consegna"))
    days_between_sale_and_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Giorni tra Vendita e Pagamento"))
    customers_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Clienti"))
    sold_products_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Prodotti Venduti"))
    sold_products_count_by_category = models.JSONField(null=True, blank=True, verbose_name=_("Conteggio Prodotti Venduti per Categoria"))
    gross_margin = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Margine Lordo"))
    average_sales_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Valore Medio Vendite"))

    class Meta:
        abstract = True

class SalesDailyAggregation(SalesAggregationMixin, DailyAggregationBase):
    def __str__(self):
        return f"Data: {self.date}"

class SalesWeeklyAggregation(SalesAggregationMixin, WeeklyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}, Settimana: {self.week}"

class SalesMonthlyAggregation(SalesAggregationMixin, MonthlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}, Mese: {self.month}"

class SalesQuarterlyAggregation(SalesAggregationMixin, QuarterlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}, Trimestre: {self.quarter}"

class SalesAnnualAggregation(SalesAggregationMixin, YearlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}"


class OrdersAggregationMixin(models.Model):
    total_orders_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Valore Totale Ordini"))
    orders_pending_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Ordini Pendenti"))
    orders_sold_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Ordini Venduti"))
    orders_delivered_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Ordini Consegnati"))
    orders_paid_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Ordini Pagati"))
    orders_cancelled_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Ordini Cancellati"))
    
    days_between_order_and_delivery = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Giorni tra Ordine e Consegna"))
    days_between_order_and_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Giorni tra Ordine e Pagamento"))
    suppliers_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Fornitori"))
    ordered_products_count = models.IntegerField(null=True, blank=True, verbose_name=_("Conteggio Prodotti Ordinati"))
    ordered_products_count_by_category = models.JSONField(null=True, blank=True, verbose_name=_("Conteggio Prodotti Ordinati per Categoria"))
    gross_margin = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Margine Lordo"))
    average_order_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Valore Medio Ordine"))
    growth_rate_previous_period = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Tasso di Crescita Periodo Precedente"))
    growth_rate_same_period_last_year = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Tasso di Crescita Stesso Periodo Anno Precedente"))

    class Meta:
        abstract = True

class OrdersDailyAggregation(OrdersAggregationMixin, DailyAggregationBase):
    def __str__(self):
        return f"Data: {self.date}"

class OrdersWeeklyAggregation(OrdersAggregationMixin, WeeklyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}, Settimana: {self.week}"

class OrdersMonthlyAggregation(OrdersAggregationMixin, MonthlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}, Mese: {self.month}"

class OrdersQuarterlyAggregation(OrdersAggregationMixin, QuarterlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}, Trimestre: {self.quarter}"

class OrdersAnnualAggregation(OrdersAggregationMixin, YearlyAggregationBase):
    def __str__(self):
        return f"Anno: {self.year}"
