from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from pdv_management.models import PDV

class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    contact = models.CharField(max_length=100, blank=True, verbose_name=_("Contatto"))
    address = models.CharField(max_length=255, blank=True, verbose_name=_("Indirizzo"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Fornitore")
        verbose_name_plural = _("Fornitori")



class Allergen(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Allergene")
        verbose_name_plural = _("Allergeni")


class Item(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    available_quantity = models.PositiveIntegerField(default=0, verbose_name=_("Quantità disponibile"))
    pdv = models.ForeignKey(PDV, on_delete=models.CASCADE, verbose_name=_("PDV"))  
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name=_("Fornitore"))

    # GenericForeignKey fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Articolo")
        verbose_name_plural = _("Articoli")


class Preparation(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    procedure = models.TextField(verbose_name=_("Procedimento"))
    pdv = models.ForeignKey(PDV, on_delete=models.CASCADE, verbose_name=_("PDV"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Preparazione")
        verbose_name_plural = _("Preparazioni")


class Ingredient(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    allergens = models.ManyToManyField('Allergen', blank=True, verbose_name=_("Allergeni"))
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Ingrediente")
        verbose_name_plural = _("Ingredienti")


class Purchase(models.Model):
    item = models.ForeignKey(Item, related_name='purchases', on_delete=models.CASCADE, verbose_name=_("Articolo"))
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name=_("Fornitore"))
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Prezzo unitario"))
    quantity = models.PositiveIntegerField(verbose_name=_("Quantità"))
    purchase_date = models.DateField(verbose_name=_("Data acquisto"))
    payment_date = models.DateField(blank=True, null=True, verbose_name=_("Data pagamento"))

    def __str__(self):
        return f"Acquisto di {self.quantity} {self.item} da {self.supplier} il {self.purchase_date}"

    class Meta:
        verbose_name = _("Acquisto")
        verbose_name_plural = _("Acquisti")
