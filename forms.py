# inventory/forms.py

from django import forms
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import Category, Product, Sale, Order

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['type']
        labels = {
            'type': _('Tipo'),
        }
        widgets = {
            'type': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].widget.attrs.update({'placeholder': _('Inserisci il tipo di categoria')})

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'code', 'category']
        labels = {
            'name': _('Nome'),
            'code': _('Codice'),
            'category': _('Categoria'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': _('Inserisci il nome del prodotto')})
        self.fields['code'].widget.attrs.update({'placeholder': _('Inserisci il codice del prodotto')})

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'sale_date', 'delivery_date', 'quantity', 'unit_price']
        labels = {
            'product': _('Prodotto'),
            'sale_date': _('Data di vendita'),
            'delivery_date': _('Data di consegna'),
            'quantity': _('Quantità'),
            'unit_price': _('Prezzo unitario'),
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs.update({'placeholder': _('Inserisci la quantità')})
        self.fields['unit_price'].widget.attrs.update({'placeholder': _('Inserisci il prezzo unitario')})

        self.fields['customer'] = forms.ModelChoiceField(
            queryset=Sale.customer.field.related_model.objects.all(),
            required=False,
            label=_("Cliente"),
            widget=forms.Select(attrs={'class': 'form-control'})
        )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'sale_date', 'delivery_date', 'quantity', 'unit_price']
        labels = {
            'product': _('Prodotto'),
            'sale_date': _('Data di ordine'),
            'delivery_date': _('Data di consegna prevista'),
            'quantity': _('Quantità'),
            'unit_price': _('Prezzo unitario'),
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs.update({'placeholder': _('Inserisci la quantità')})
        self.fields['unit_price'].widget.attrs.update({'placeholder': _('Inserisci il prezzo unitario')})

        self.fields['supplier'] = forms.ModelChoiceField(
            queryset=Order.supplier.field.related_model.objects.all(),
            required=False,
            label=_("Fornitore"),
            widget=forms.Select(attrs={'class': 'form-control'})
        )