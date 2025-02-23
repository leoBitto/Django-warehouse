from django import forms
from .models.base import ProductCategory, Product, ProductSupplierCode, ProductImage

class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'parent', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome della categoria'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrizione'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 
            'category', 
            'stock_quantity', 
            'description', 
            'notes', 
            'is_visible'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome del prodotto'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantità in stock'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrizione'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Note interne'}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProductSupplierCodeForm(forms.ModelForm):
    class Meta:
        model = ProductSupplierCode
        fields = [
            'product', 
            'supplier', 
            'external_code', 
            'description'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'external_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Codice fornitore'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descrizione fornitore'}),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['product', 'image', 'is_primary']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
