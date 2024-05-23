from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Supplier, Item, Ingredient, Purchase

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact', 'address']
        labels = {
            'name': _('Nome'),
            'contact': _('Contatto'),
            'address': _('Indirizzo'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': _('Inserisci il nome')})
        self.fields['contact'].widget.attrs.update({'placeholder': _('Inserisci il contatto')})
        self.fields['address'].widget.attrs.update({'placeholder': _('Inserisci l\'indirizzo')})

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'available_quantity', 'pdv']
        labels = {
            'name': _('Nome'),
            'available_quantity': _('Quantità disponibile'),
            'pdv': _('PDV'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'available_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'pdv': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': _('Inserisci il nome')})
        self.fields['available_quantity'].widget.attrs.update({'placeholder': _('Inserisci la quantità disponibile')})

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'available_quantity', 'pdv', 'allergens']
        labels = {
            'name': _('Nome'),
            'available_quantity': _('Quantità disponibile'),
            'pdv': _('PDV'),
            'allergens': _('Allergeni'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'available_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'pdv': forms.Select(attrs={'class': 'form-control'}),
            'allergens': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': _('Inserisci il nome')})
        self.fields['available_quantity'].widget.attrs.update({'placeholder': _('Inserisci la quantità disponibile')})

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['item', 'supplier', 'unit_price', 'quantity', 'purchase_date', 'payment_date']
        labels = {
            'item': _('Articolo'),
            'supplier': _('Fornitore'),
            'unit_price': _('Prezzo unitario'),
            'quantity': _('Quantità'),
            'purchase_date': _('Data acquisto'),
            'payment_date': _('Data pagamento'),
        }
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_price'].widget.attrs.update({'placeholder': _('Inserisci il prezzo unitario')})
        self.fields['quantity'].widget.attrs.update({'placeholder': _('Inserisci la quantità')})
        self.fields['purchase_date'].widget.attrs.update({'placeholder': _('Seleziona la data di acquisto')})
        self.fields['payment_date'].widget.attrs.update({'placeholder': _('Seleziona la data di pagamento')})
