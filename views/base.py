# inventory/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models.base import ProductCategory, Product, Sale, Order, ProductImage
from ..forms import ProductCategoryForm, ProductForm, SaleForm, OrderForm, ProductImageForm
from django.contrib import messages
import csv
from django.http import HttpResponse, Http404
from datetime import datetime
from crm.models.base import *  


# inventory/views.py

class ProductCategoryView(LoginRequiredMixin, View):
    template_name = 'inventory/product_category.html'

    def get(self, request, *args, **kwargs):
        categories = ProductCategory.objects.all()
        category_info = []

        # Creare un modulo per ogni categoria
        for category in categories:
            form = ProductCategoryForm(instance=category)
            category_info.append({'category': category, 'form': form})

        # Aggiungere un modulo vuoto per la creazione di nuove categorie
        create_form = ProductCategoryForm()

        return render(request, self.template_name, {
            'category_info': category_info,
            'create_form': create_form,
        })

    def post(self, request, *args, **kwargs):
        if 'create_category' in request.POST:
            create_form = ProductCategoryForm(request.POST)
            if create_form.is_valid():
                create_form.save()
                messages.success(request, 'Categoria creata con successo!')
                return redirect('inventory:product_category_view')
            else:
                for field, errors in create_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")

        elif 'update_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(ProductCategory, id=category_id)
            form = ProductCategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, 'Categoria aggiornata con successo!')
                return redirect('inventory:product_category_view')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")

        elif 'delete_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(ProductCategory, id=category_id)
            category.delete()
            messages.success(request, 'Categoria eliminata con successo!')
            return redirect('inventory:product_category_view')

        # Se si arriva qui, non è stato fatto nulla di valido
        categories = ProductCategory.objects.all()
        category_info = []

        for category in categories:
            form = ProductCategoryForm(instance=category)
            category_info.append({'category': category, 'form': form})

        create_form = ProductCategoryForm()

        return render(request, self.template_name, {
            'category_info': category_info,
            'create_form': create_form,
        })


class ProductView(LoginRequiredMixin, View):
    template_name = 'inventory/product.html'
    
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        product_info = []

        # Creare un modulo per ogni prodotto
        for product in products:
            form = ProductForm(instance=product)
            product_info.append({'product': product, 'form': form})

        # Aggiungere un modulo vuoto per la creazione di nuovi prodotti
        create_form = ProductForm()

        return render(request, self.template_name, {
            'product_forms': product_info,
            'create_form': create_form,
        })

    def post(self, request, *args, **kwargs):
        if 'create_product' in request.POST:
            create_form = ProductForm(request.POST, request.FILES)
            if create_form.is_valid():
                create_form.save()
                messages.success(request, 'Prodotto creato con successo!')
                return redirect('inventory:product_view')
            else:
                for field, errors in create_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")

        elif 'update_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Prodotto aggiornato con successo!')
                return redirect('inventory:product_view')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")

        elif 'delete_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            messages.success(request, 'Prodotto eliminato con successo!')
            return redirect('inventory:product_view')

        # Ricarica i prodotti e i form se non è stato fatto nulla di valido
        products = Product.objects.all()
        product_info = []
        for product in products:
            form = ProductForm(instance=product)
            product_info.append({'product': product, 'form': form})

        create_form = ProductForm()

        return render(request, self.template_name, {
            'product_forms': product_info,
            'create_form': create_form,
        })


class ProductDetailView(LoginRequiredMixin, View):
    template_name = 'inventory/product_detail.html'

    def get(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        product_form = ProductForm(instance=product)
        image_form = ProductImageForm()

        orders = product.order_transactions.all()
        sales = product.sale_transactions.all()

        return render(request, self.template_name, {
            'product': product,
            'product_form': product_form,
            'image_form': image_form,
            'orders': orders,
            'sales': sales,
        })

    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        image_form = ProductImageForm(request.POST, request.FILES)

        if 'update_product' in request.POST:
            if product_form.is_valid():
                product_form.save()
                messages.success(request, 'Prodotto aggiornato con successo!')
                return redirect('inventory:product_detail', product_id=product.id)
            else:
                for field, errors in product_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")

        elif 'delete_product' in request.POST:
            product.delete()
            messages.success(request, 'Prodotto eliminato con successo!')
            return redirect('inventory:product_view')

        elif 'add_images' in request.POST:
            if image_form.is_valid():
                image = image_form.save(commit=False)
                image.product = product
                image.save()
                messages.success(request, 'Immagine aggiunta con successo!')
                return redirect('inventory:product_detail', product_id=product.id)
            else:
                for form in image_form:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"Errore nel campo immagine '{field}': {error}")

        elif 'delete_image' in request.POST:
            image_id = request.POST.get('image_id')
            image = get_object_or_404(ProductImage, id=image_id, product=product)
            image.delete()
            messages.success(request, 'Immagine eliminata con successo!')
            return redirect('inventory:product_detail', product_id=product.id)

        return render(request, self.template_name, {
            'product': product,
            'product_form': product_form,
            'image_form': image_form,
        })


class InvoiceDetailView(View):
    template_name = 'inventory/invoice_detail.html'

    def get(self, request, *args, **kwargs):
        invoice_number = self.kwargs['invoice_number']
        invoice_type = self.kwargs['invoice_type']

        if invoice_type == 'order':
            objects = Order.objects.filter(order_invoice_number=invoice_number)
            if not objects.exists():
                raise Http404("Fattura ordine non trovata")
            context = self.get_order_context(objects)
        elif invoice_type == 'sale':
            objects = Sale.objects.filter(sale_invoice_number=invoice_number)
            if not objects.exists():
                raise Http404("Fattura vendita non trovata")
            context = self.get_sale_context(objects)
        else:
            raise Http404("Tipo di fattura non valido")

        return render(request, self.template_name, context)

    def get_order_context(self, orders):
        context = {
            'orders': orders,
            'supplier': get_object_or_404(Supplier, id=orders.first().supplier_id),
            'total_value': sum(order.unit_price * order.quantity for order in orders),
            'invoice_type': 'order',
        }
        return context

    def get_sale_context(self, sales):
        context = {
            'sales': sales,
            'customer': get_object_or_404(Customer, id=sales.first().customer_id),
            'total_value': sum(sale.unit_price * sale.quantity for sale in sales),
            'invoice_type': 'sale',
        }
        return context


class DownloadStockDataCSV(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        # Creazione della risposta HTTP con tipo di contenuto CSV
        response = HttpResponse(content_type='text/csv')
        current_date = datetime.now().strftime("%Y-%m-%d")
        response['Content-Disposition'] = f'attachment; filename="magazzino_{current_date}.csv"'

        # Scrittura del contenuto CSV
        writer = csv.writer(response)
        writer.writerow(['Nome Prodotto', 'Quantità in Magazzino', 'Valore Stock'])

        products = Product.objects.all()
        for product in products:
            stock_value = product.stock_quantity * product.average_purchase_price
            writer.writerow([product.name, product.stock_quantity, f'€{stock_value:.2f}'])

        return response
    


class SaleListView(LoginRequiredMixin, View):
    template_name = 'inventory/sale.html'

    def get(self, request, *args, **kwargs):
        sales = Sale.objects.order_by('-sale_date')[:100]  # Mostra le ultime 100 vendite
        create_form = SaleForm()

        return render(request, self.template_name, {
            'sales': sales,
            'create_form': create_form,
        })

    def post(self, request, *args, **kwargs):
        if 'create_sale' in request.POST:
            create_form = SaleForm(request.POST, request.FILES)
            if create_form.is_valid():
                create_form.save()
                messages.success(request, 'Vendita registrata con successo!')
            else:
                for field, errors in create_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
            return redirect('inventory:sale_list')
    

class SaleDetailView(LoginRequiredMixin, View):
    template_name = 'inventory/sale_detail.html'

    def get(self, request, *args, **kwargs):
        sale_id = kwargs.get('sale_id')
        sale = get_object_or_404(Sale, id=sale_id)
        form = SaleForm(instance=sale)

        return render(request, self.template_name, {
            'sale': sale,
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        sale_id = request.POST.get('sale_id')
        sale = get_object_or_404(Sale, id=sale_id)

        if 'update_sale' in request.POST:
            form = SaleForm(request.POST, request.FILES, instance=sale)
            if form.is_valid():
                form.save()
                messages.success(request, 'Vendita aggiornata con successo!')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
            return redirect('inventory:sale_list')

        elif 'delete_sale' in request.POST:
            sale.delete()
            messages.success(request, 'Vendita eliminata con successo!')
            return redirect('inventory:sale_list')


class OrderListView(LoginRequiredMixin, View):
    template_name = 'inventory/order.html'

    def get(self, request, *args, **kwargs):
        orders = Order.objects.order_by('-sale_date')[:100]  # Mostra le ultime 100 vendite
        create_form = OrderForm()

        return render(request, self.template_name, {
            'orders': orders,
            'create_form': create_form,
        })

    def post(self, request, *args, **kwargs):
        if 'create_order' in request.POST:
            create_form = OrderForm(request.POST, request.FILES)
            if create_form.is_valid():
                create_form.save()
                messages.success(request, 'Ordine creato con successo!')
                return redirect('inventory:order_list')
            else:
                for field, errors in create_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
        return redirect('inventory:order_list')
    

class OrderDetailView(LoginRequiredMixin, View):
    template_name = 'inventory/order_detail.html'

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        form = OrderForm(instance=order)

        return render(request, self.template_name, {
            'order': order,
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)

        if 'update_order' in request.POST:
            form = OrderForm(request.POST, request.FILES, instance=order)
            if form.is_valid():
                form.save()
                messages.success(request, 'Ordine aggiornato con successo!')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
            return redirect('inventory:order_list')

        elif 'delete_order' in request.POST:
            order.delete()
            messages.success(request, 'Ordine eliminato con successo!')
            return redirect('inventory:order_list')
