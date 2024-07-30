# INVENTORY models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

if 'crm' in settings.INSTALLED_APPS:
    from crm.models import Customer, Supplier
else:
    Customer = None
    Supplier = None

class Category(models.Model):
    type = models.CharField(_("tipo"), max_length=50)

    class Meta:
        verbose_name = _("categoria")
        verbose_name_plural = _("categorie")

    def __str__(self):
        return self.type

class Product(models.Model):
    name = models.CharField(_("nome"), max_length=100)
    code = models.CharField(_("codice"), max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name=_("categoria"))

    class Meta:
        verbose_name = _("prodotto")
        verbose_name_plural = _("prodotti")

    def __str__(self):
        return f"{self.name} ({self.code})"

class Transaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='%(class)s_transactions', verbose_name=_("prodotto"))
    sale_date = models.DateField(_("data vendita"))
    delivery_date = models.DateField(_("data consegna"))
    quantity = models.IntegerField(_("pezzi"))
    unit_price = models.DecimalField(_("prezzo unitario"), max_digits=10, decimal_places=2)

    class Meta:
        abstract = True

class Sale(Transaction):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='sales', verbose_name=_("cliente"))

    class Meta:
        verbose_name = _("vendita")
        verbose_name_plural = _("vendite")

    def __str__(self):
        return _("Vendita a {customer} - {product}").format(customer=self.customer.name, product=self.product.name)

class Order(Transaction):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True, related_name='orders', verbose_name=_("fornitore"))

    class Meta:
        verbose_name = _("ordine")
        verbose_name_plural = _("ordini")

    def __str__(self):
        return _("Ordine da {supplier} - {product}").format(supplier=self.supplier.name, product=self.product.name)
