from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete
from decimal import Decimal
import uuid

# Lazy loading dei modelli da altre app
if 'crm' in settings.INSTALLED_APPS:
    from crm.models.base import Company
else:
    Company = None

class ProductCategory(models.Model):
    """Categoria di prodotti con possibilità di categorie annidate"""
    name = models.CharField(_("nome"), max_length=50)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_("categoria padre")
    )
    description = models.TextField(_("descrizione"), blank=True)

    class Meta:
        verbose_name = _("categoria")
        verbose_name_plural = _("categorie")
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    """Modello principale per i prodotti"""
    # Dati principali
    name = models.CharField(_("nome"), max_length=200)
    internal_code = models.CharField(
        _("codice interno"),
        max_length=50,
        unique=True,
        db_index=True,
        editable=False
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_("categoria")
    )

    # Gestione magazzino
    stock_quantity = models.DecimalField(
        _("quantità in stock"),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Dettagli prodotto
    description = models.TextField(_("descrizione"), blank=True)
    notes = models.TextField(_("note interne"), blank=True)
    is_visible = models.BooleanField(_("visibile nel sito web"), default=False)
    created_at = models.DateTimeField(_("data creazione"), auto_now_add=True)
    updated_at = models.DateTimeField(_("ultima modifica"), auto_now=True)

    class Meta:
        verbose_name = _("prodotto")
        verbose_name_plural = _("prodotti")
        indexes = [
            models.Index(fields=['name', 'internal_code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.internal_code})"

    def save(self, *args, **kwargs):
        if not self.internal_code:
            self.internal_code = self.generate_internal_code()
        super().save(*args, **kwargs)

    def generate_internal_code(self):
        """Genera un codice interno univoco per il prodotto"""
        return f"PROD-{uuid.uuid4().hex[:8].upper()}"

    def update_stock(self, quantity_delta):
        """
        Aggiorna la quantità in stock del prodotto

        Args:
            quantity_delta: la variazione di quantità (positiva per aumenti, negativa per diminuzioni)
        """
        self.stock_quantity += quantity_delta
        self.save()

    def calculate_average_purchase_price(self):
        """Calcola il prezzo medio di acquisto dalle righe delle fatture"""
        total_price = Decimal('0')
        total_quantity = 0
        for line in self.invoiceline_set.filter(invoice__invoice_type='IN'):
            total_price += line.unit_price * line.quantity
            total_quantity += line.quantity
        return total_price / total_quantity if total_quantity > 0 else Decimal('0')

    def calculate_average_sales_price(self):
        """Calcola il prezzo medio di vendita dalle righe delle fatture"""
        total_price = Decimal('0')
        total_quantity = 0
        for line in self.invoiceline_set.filter(invoice__invoice_type='OUT'):
            total_price += line.unit_price * line.quantity
            total_quantity += line.quantity
        return total_price / total_quantity if total_quantity > 0 else Decimal('0')

    @property
    def average_purchase_price(self):
        return self.calculate_average_purchase_price()

    @property
    def average_sales_price(self):
        return self.calculate_average_sales_price()

    @property
    def gross_margin(self):
        return (self.average_sales_price - self.average_purchase_price) if self.average_sales_price and self.average_purchase_price else Decimal('0')

    @property
    def net_margin(self):
        """Calcola il margine netto considerando l'IVA"""
        total_vat = Decimal('0')
        total_quantity = 0
        for line in self.invoiceline_set.filter(invoice__invoice_type='OUT'):
            total_vat += line.vat_rate * line.quantity
            total_quantity += line.quantity
        average_vat = total_vat / total_quantity if total_quantity > 0 else Decimal('0')
        return self.gross_margin - average_vat

    def get_supplier_codes(self):
        """Restituisce un dizionario di codici prodotto per fornitore"""
        return {
            code.supplier: code.external_code
            for code in self.supplier_codes.all()
        }

class ProductSupplierCode(models.Model):
    """
    Mappatura tra codici prodotto dei fornitori e prodotti interni.
    Ogni prodotto può avere più codici, uno per fornitore.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='supplier_codes',
        verbose_name=_("prodotto")
    )
    supplier = models.ForeignKey(
        'crm.Company',
        on_delete=models.CASCADE,
        related_name='product_codes',
        verbose_name=_("fornitore")
    )
    external_code = models.CharField(
        _("codice fornitore"),
        max_length=50,
        help_text=_("Codice utilizzato dal fornitore per questo prodotto")
    )
    description = models.TextField(
        _("descrizione fornitore"),
        blank=True,
        help_text=_("Descrizione del prodotto utilizzata dal fornitore")
    )

    class Meta:
        verbose_name = _("codice fornitore")
        verbose_name_plural = _("codici fornitori")
        unique_together = ['supplier', 'external_code']  # Un codice deve essere univoco per fornitore
        indexes = [
            models.Index(fields=['supplier', 'external_code']),
        ]

    def __str__(self):
        return f"{self.supplier.name}: {self.external_code}"

class ProductImage(models.Model):
    """Immagini associate ai prodotti"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_("prodotto")
    )
    image = models.ImageField(_("immagine"), upload_to='products/')
    is_primary = models.BooleanField(_("immagine principale"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("immagine prodotto")
        verbose_name_plural = _("immagini prodotti")
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"Immagine di {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Assicura che ci sia solo un'immagine principale
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)

@receiver(post_delete, sender=ProductImage)
def delete_image_file(sender, instance, **kwargs):
    """Elimina il file dell'immagine quando viene eliminata l'istanza"""
    if instance.image:
        instance.image.delete(False)
