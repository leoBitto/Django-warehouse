from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from pdv_management.models import PDV

class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    contact = models.CharField(max_length=100, blank=True, verbose_name=_("Contatto"))
    address = models.CharField(max_length=255, blank=True, verbose_name=_("Indirizzo"))

    def _str_(self):
        return self.name

    class Meta:
        verbose_name = _("Fornitore")
        verbose_name_plural = _("Fornitori")



class Allergen(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))

    def _str_(self):
        return self.name

    class Meta:
        verbose_name = _("Allergene")
        verbose_name_plural = _("Allergeni")

class ItemBase(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogrammi'),
        ('unit', 'Unità'),
        # Aggiungi altre unità di misura se necessario
    ]
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    available_quantity = models.PositiveIntegerField(default=0, verbose_name=_("Quantità disponibile"))
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='unit', verbose_name=_("Unità di misura"))
    pdv = models.ForeignKey(PDV, on_delete=models.CASCADE, verbose_name=_("PDV"))  
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name=_("Fornitore"))

    def _str_(self):
        return f"{self.name} ({self.available_quantity} {self.get_unit_display()})"

    class Meta:
        abstract = True


class Item(ItemBase):

    class Meta:
        verbose_name = _("Articolo")
        verbose_name_plural = _("Articoli")

class Ingredient(ItemBase):
    allergens = models.ManyToManyField('Allergen', blank=True, verbose_name=_("Allergeni"))

    class Meta:
        verbose_name = _("Ingrediente")
        verbose_name_plural = _("Ingredienti")



class Preparation(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    procedure = models.TextField(verbose_name=_("Procedimento"), blank=True, null=True)
    pdv = models.ForeignKey(PDV, on_delete=models.CASCADE, verbose_name=_("PDV"))
    ingredients = models.ManyToManyField(Ingredient, through='PreparationIngredient')


    def _str_(self):
        return self.name

    class Meta:
        verbose_name = _("Preparazione")
        verbose_name_plural = _("Preparazioni")


class PreparationIngredient(models.Model):
    preparation = models.ForeignKey(Preparation, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50, verbose_name=_("Quantità"))

    class Meta:
        verbose_name = _("Quantità Ingrediente")
        verbose_name_plural = _("Quantità Ingredienti")


class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name=_("Fornitore"))
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Prezzo unitario"))
    quantity = models.PositiveIntegerField(verbose_name=_("Quantità"))
    purchase_date = models.DateField(verbose_name=_("Data acquisto"))
    payment_date = models.DateField(blank=True, null=True, verbose_name=_("Data pagamento"))

    # GenericForeignKey per supportare sia Item che Ingredient
    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=models.Q(app_label='inventory', model='item') | models.Q(app_label='inventory', model='ingredient'),
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        if self.object_name:
            model_class = ContentType.objects.get(model=self.object_name).model_class()
            self.content_type = ContentType.objects.get_for_model(model_class)
        super().save(*args, **kwargs)

    def _str_(self):
        return f"Acquisto di {self.quantity} {self.item} da {self.supplier} il {self.purchase_date}"

    class Meta:
        verbose_name = _("Acquisto")
        verbose_name_plural = _("Acquisti")