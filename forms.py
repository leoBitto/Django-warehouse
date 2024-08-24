from django import forms
from .models.base import Category, Product, Sale, Order
from decimal import Decimal

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent']
        widgets = {
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 
            'stock_quantity', 'unit_price', 'image', 'is_visible', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price < Decimal('0'):
            raise forms.ValidationError('Il prezzo unitario non può essere negativo.')
        return unit_price
    
    def clean(self):
        cleaned_data = super().clean()
        
        is_visible = cleaned_data.get('is_visible')
        image = cleaned_data.get('image')
        description = cleaned_data.get('description')

        if is_visible and (not image or not description):
            raise forms.ValidationError(
                'Il prodotto può essere reso visibile solo se è presente un\'immagine e una descrizione.'
            )

        return cleaned_data




class TransactionForm(forms.ModelForm):
    class Meta:
        abstract = True
        fields = [
            'product', 'sale_date', 'delivery_date', 
            'payment_date', 'quantity', 'unit_price', 
            'status', 'invoice', 'delivery_note'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format=('%d/%m/%Y')),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format=('%d/%m/%Y')),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format=('%d/%m/%Y')),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'invoice': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'delivery_note': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Imposta le scelte per lo stato, inclusa solo l'opzione "Annullato" e una vuota
        self.fields['status'].choices = [
            ('pending', 'In Attesa'),
            ('cancelled', 'Annullato'),
        ]

    def clean(self):
        cleaned_data = super().clean()
        sale_date = cleaned_data.get('sale_date')
        delivery_date = cleaned_data.get('delivery_date')
        payment_date = cleaned_data.get('payment_date')
        unit_price = cleaned_data.get('unit_price')
        status = cleaned_data.get('status')

        # Validazione dei prezzi
        if unit_price is not None and unit_price < Decimal('0'):
            self.add_error('unit_price', 'Il prezzo unitario non può essere negativo.')

        if status != 'cancelled':
            if sale_date and delivery_date and sale_date > delivery_date:
                self.add_error('sale_date', 'La data di vendita deve essere prima della data di consegna.')

            if sale_date and payment_date and payment_date < sale_date:
                self.add_error('payment_date', 'La data di pagamento non può essere anteriore alla data di vendita.')

            if status == 'sold' and not sale_date:
                self.add_error('sale_date', 'La data di vendita è obbligatoria per lo stato "Venduto".')
            elif status == 'delivered' and not delivery_date:
                self.add_error('delivery_date', 'La data di consegna è obbligatoria per lo stato "Consegnato".')
            elif status == 'paid' and not payment_date:
                self.add_error('payment_date', 'La data di pagamento è obbligatoria per lo stato "Pagato".')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Se non è stato selezionato uno stato, imposta lo stato basato sulle date
        if not instance.status:
            if instance.sale_date and not instance.delivery_date and not instance.payment_date:
                instance.status = 'sold'
            elif instance.sale_date and instance.delivery_date and not instance.payment_date:
                instance.status = 'delivered'
            elif instance.sale_date and instance.delivery_date and instance.payment_date:
                instance.status = 'paid'
            else:
                instance.status = 'pending'  # Imposta uno stato predefinito se nessuna delle condizioni è soddisfatta

        if commit:
            instance.save()
        return instance

class SaleForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        model = Sale
        fields = TransactionForm.Meta.fields + ['customer']
        widgets = {
            **TransactionForm.Meta.widgets,
            'customer': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        
        if product and quantity:
            if quantity > product.stock_quantity:
                self.add_error('quantity', 'Quantità richiesta non disponibile in stock.')
        
        return cleaned_data

class OrderForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        model = Order
        fields = TransactionForm.Meta.fields + ['supplier']
        widgets = {
            **TransactionForm.Meta.widgets,
            'supplier': forms.Select(attrs={'class': 'form-control'}),
        }