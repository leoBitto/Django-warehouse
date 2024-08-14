# inventory/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Category, Product, Sale, Order
from .forms import CategoryForm, ProductForm, SaleForm, OrderForm
from django.contrib import messages

# inventory/views.py

class CategoryView(LoginRequiredMixin, View):
    template_name = 'inventory/category.html'

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        category_info = []

        # Creare un modulo per ogni categoria
        for category in categories:
            form = CategoryForm(instance=category)
            category_info.append({'category': category, 'form': form})

        # Aggiungere un modulo vuoto per la creazione di nuove categorie
        create_form = CategoryForm()

        return render(request, self.template_name, {
            'category_info': category_info,
            'create_form': create_form,
        })

    def post(self, request, *args, **kwargs):
        if 'create_category' in request.POST:
            create_form = CategoryForm(request.POST)
            if create_form.is_valid():
                create_form.save()
                messages.success(request, 'Categoria creata con successo!')
                return redirect('inventory:category_view')
            else:
                for field, errors in create_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")

        elif 'update_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, 'Categoria aggiornata con successo!')
                return redirect('inventory:category_view')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")

        elif 'delete_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            messages.success(request, 'Categoria eliminata con successo!')
            return redirect('inventory:category_view')

        # Se si arriva qui, non è stato fatto nulla di valido
        categories = Category.objects.all()
        category_info = []

        for category in categories:
            form = CategoryForm(instance=category)
            category_info.append({'category': category, 'form': form})

        create_form = CategoryForm()

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
        form = ProductForm(instance=product)

        return render(request, self.template_name, {
            'product': product,
            'form': form
        })

    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)

        if 'update_product' in request.POST:
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Prodotto aggiornato con successo!')
                return redirect('inventory:product_detail', product_id=product.id)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")

        elif 'delete_product' in request.POST:
            product.delete()
            messages.success(request, 'Prodotto eliminato con successo!')
            return redirect('inventory:product_view')
        
        form = ProductForm(request.POST, request.FILES, instance=product)

        return render(request, self.template_name, {
            'product': product,
            'form': form
        })



class SaleView(LoginRequiredMixin, View):
    template_name = 'inventory/sale.html'
    
    def get(self, request, *args, **kwargs):
        sales = Sale.objects.order_by('-sale_date')[:50]
        sales_info = []

        # Creare un modulo per ogni vendita
        for sale in sales:
            form = SaleForm(instance=sale)
            sales_info.append({'sale': sale, 'form': form})

        # Aggiungere un modulo vuoto per la creazione di nuove vendite
        create_form = SaleForm()

        return render(request, self.template_name, {
            'sale_forms': sales_info,
            'create_form': create_form,
        })

    def post(self, request, *args, **kwargs):
        if 'create_sale' in request.POST:
            create_form = SaleForm(request.POST, request.FILES)
            if create_form.is_valid():
                create_form.save()
                messages.success(request, 'Vendita registrata con successo!')
                return redirect('inventory:sale_view')
            else:
                for field, errors in create_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")


        elif 'update_sale' in request.POST:
            sale_id = request.POST.get('sale_id')
            sale = get_object_or_404(Sale, id=sale_id)
            form = SaleForm(request.POST, request.FILES, instance=sale)

            if form.is_valid():
                form.save()
                messages.success(request, 'Vendita aggiornata con successo!')
                return redirect('inventory:sale_view')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")


        elif 'delete_sale' in request.POST:
            sale_id = request.POST.get('sale_id')
            sale = get_object_or_404(Sale, id=sale_id)
            sale.delete()
            messages.success(request, 'Vendita eliminata con successo!')
            return redirect('inventory:sale_view')

        # Ricarica le vendite e i form se non è stato fatto nulla di valido
        sales = Sale.objects.all()
        sales_info = []
        for sale in sales:
            form = SaleForm(instance=sale)
            sales_info.append({'sale': sale, 'form': form})

        create_form = SaleForm()

        return render(request, self.template_name, {
            'sale_forms': sales_info,
            'create_form': create_form
        })
    

class OrderView(LoginRequiredMixin, View):
    template_name = 'inventory/order.html'

    def get(self, request, *args, **kwargs):
        orders = Order.objects.order_by('-sale_date')[:50]
        orders_info = []

        # Creare un modulo per ogni ordine
        for order in orders:
            form = OrderForm(instance=order)
            orders_info.append({'order': order, 'form': form})

        # Aggiungere un modulo vuoto per la creazione di nuovi ordini
        create_form = OrderForm()

        return render(request, self.template_name, {
            'order_forms': orders_info,
            'create_form': create_form,
        })

    def post(self, request, *args, **kwargs):
        if 'create_order' in request.POST:
            create_form = OrderForm(request.POST, request.FILES)

            if create_form.is_valid():
                order = create_form.save()
                messages.success(request, 'Ordine creato con successo!')
                return redirect('inventory:order_view')
            else:
                for field, errors in create_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")

        elif 'update_order' in request.POST:
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id)
            form = OrderForm(request.POST, request.FILES, instance=order)

            if form.is_valid():
                form.save()
                messages.success(request, 'Ordine aggiornato con successo!')
                return redirect('inventory:order_view')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")

        elif 'delete_order' in request.POST:
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id)
            order.delete()
            messages.success(request, 'Ordine eliminato con successo!')
            return redirect('inventory:order_view')

        # Ricarica gli ordini e i form se non è stato fatto nulla di valido
        orders = Order.objects.all()
        orders_info = []
        for order in orders:
            form = OrderForm(instance=order)
            orders_info.append({'order': order, 'form': form})

        create_form = OrderForm()

        return render(request, self.template_name, {
            'order_forms': orders_info,
            'create_form': create_form
        })