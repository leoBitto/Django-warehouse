from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
import uuid
from decimal import Decimal

if 'crm' in settings.INSTALLED_APPS:
    from crm.models import Customer, Supplier
else:
    Customer = None
    Supplier = None

class Category(models.Model):
    name = models.CharField(_("tipo"), max_length=50)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories', verbose_name=_("categoria padre"))

    class Meta:
        verbose_name = _("categoria")
        verbose_name_plural = _("categorie")

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(_("nome"), max_length=100)
    internal_code = models.CharField(_("codice interno"), max_length=50, unique=True, db_index=True, editable=False)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name=_("categoria"))
    stock_quantity = models.PositiveIntegerField(_("quantità in stock"), default=0)
    unit_price = models.DecimalField(_("prezzo unitario"), max_digits=10, decimal_places=2)
    image = models.ImageField(_("immagine"), upload_to='products/', blank=True, null=True)
    is_visible = models.BooleanField(_("visibile nel sito web"), default=True)
    description = models.TextField(_("descrizione"), blank=True, null=True)

    class Meta:
        verbose_name = _("prodotto")
        verbose_name_plural = _("prodotti")
        indexes = [
            models.Index(fields=['name', 'internal_code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.internal_code})"
    
    def clean(self):
        if self.unit_price < Decimal('0'):
            raise ValidationError(_('Il prezzo unitario non può essere negativo.'))

    def save(self, *args, **kwargs):
        if not self.internal_code:
            self.internal_code = self.generate_internal_code()
        super().save(*args, **kwargs)

    def generate_internal_code(self):
        return f"PROD-{uuid.uuid4().hex[:8].upper()}"

    def update_stock(self, quantity_change):
        if self.stock_quantity + quantity_change < 0:
            raise ValidationError(_('Quantità di stock insufficiente per l\'operazione.'))
        self.stock_quantity += quantity_change
        self.save()

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', _('In attesa')),
        ('completed', _('Completata')),
        ('cancelled', _('Annullata')),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='%(class)s_transactions', verbose_name=_("prodotto"))
    sale_date = models.DateField(_("data vendita"), blank=True, null=True)
    delivery_date = models.DateField(_("data consegna"), blank=True, null=True)
    payment_date = models.DateField(_("data pagamento"), blank=True, null=True)
    quantity = models.PositiveIntegerField(_("pezzi"))
    unit_price = models.DecimalField(_("prezzo unitario"), max_digits=10, decimal_places=2)
    status = models.CharField(_("stato"), max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        abstract = True

    def clean(self):
        if self.sale_date and self.delivery_date and self.sale_date > self.delivery_date:
            raise ValidationError(_('La data di vendita deve essere prima della data di consegna.'))
        if self.sale_date and self.payment_date and self.payment_date < self.sale_date:
            raise ValidationError(_('La data di pagamento non può essere anteriore alla data di vendita.'))
        if self.unit_price < Decimal('0'):
            raise ValidationError(_('Il prezzo unitario non può essere negativo.'))

    @property
    def total_price(self):
        return self.quantity * self.unit_price



class Sale(Transaction):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='sales', verbose_name=_("cliente"))

    class Meta:
        verbose_name = _("vendita")
        verbose_name_plural = _("vendite")

    def __str__(self):
        return _("Vendita a {customer} - {product}").format(customer=self.customer.name if self.customer else 'N/A', product=self.product.name)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk is None:  # se è una nuova vendita
                self.product.update_stock(-self.quantity)
            elif self.status == 'cancelled' and self._state.adding is False:
                # Se stiamo cancellando una vendita esistente
                original = Sale.objects.get(pk=self.pk)
                if original.status != 'cancelled':
                    self.product.update_stock(original.quantity)
            super().save(*args, **kwargs)


class Order(Transaction):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True, related_name='orders', verbose_name=_("fornitore"))

    class Meta:
        verbose_name = _("ordine")
        verbose_name_plural = _("ordini")

    def __str__(self):
        return _("Ordine da {supplier} - {product}").format(supplier=self.supplier.name if self.supplier else 'N/A', product=self.product.name)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk is None:  # se è un nuovo ordine
                self.product.update_stock(self.quantity)
            elif self.status == 'cancelled' and self._state.adding is False:
                # Se stiamo cancellando un ordine esistente
                original = Order.objects.get(pk=self.pk)
                if original.status != 'cancelled':
                    self.product.update_stock(-original.quantity)
            super().save(*args, **kwargs)