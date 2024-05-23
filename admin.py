from django.contrib import admin
from django import forms
from .models import Supplier, Item, Ingredient, Preparation, Allergen, PreparationIngredient, Purchase

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'address')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'available_quantity', 'unit', 'pdv', 'supplier')

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'available_quantity', 'unit', 'pdv', 'supplier')
    filter_horizontal = ('allergens',)

@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Preparation)
class PreparationAdmin(admin.ModelAdmin):
    list_display = ('name', 'procedure', 'pdv')


@admin.register(PreparationIngredient)
class PreparationIngredientAdmin(admin.ModelAdmin):
    list_display = ('preparation', 'ingredient', 'quantity')


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        exclude = ['content_type'] 

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        # Ottieni tutti gli oggetti Item e Ingredient e costruisci una lista di tuple (id, nome)
        item_choices = [(item.id, str(item)) for item in Item.objects.all()]
        ingredient_choices = [(ingredient.id, str(ingredient)) for ingredient in Ingredient.objects.all()]
        # Unisci le liste di scelta per Item e Ingredient
        all_choices = item_choices + ingredient_choices
        # Aggiungi il campo di scelta per gli oggetti Item e Ingredient
        self.fields['object_id'] = forms.ChoiceField(choices=all_choices)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm

    # Override per salvare l'oggetto corretto basato sul valore selezionato nel campo object_id
    def save_model(self, request, obj, form, change):
        content_type = form.cleaned_data['content_type']
        obj.content_object = content_type.model_class().objects.get(pk=form.cleaned_data['object_id'])
        super().save_model(request, obj, form, change)