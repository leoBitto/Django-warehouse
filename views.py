# inventory/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Category, Product, Sale, Order
from .forms import CategoryForm, ProductForm, SaleForm, OrderForm
from django.contrib import messages

class CategoryView(LoginRequiredMixin, View):
    template_name = 'inventory/category.html'
    
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        category_form = CategoryForm()
        return render(request, self.template_name, {
            'categories': categories,
            'category_form': category_form,
        })

    def post(self, request, *args, **kwargs):
        if 'create_category' in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, 'Categoria creata con successo!')
                return redirect('inventory:category_view')
            else:
                for field, errors in category_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
        
        elif 'update_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category_form = CategoryForm(request.POST, instance=category)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, 'Categoria aggiornata con successo!')
                return redirect('inventory:category_view')
            else:
                for field, errors in category_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
        
        elif 'delete_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            messages.success(request, 'Categoria eliminata con successo!')
            return redirect('inventory:category_view')
        
        categories = Category.objects.all()
        return render(request, self.template_name, {
            'categories': categories,
            'category_form': CategoryForm(),
        })


class ProductView(LoginRequiredMixin, View):
    template_name = 'inventory/product.html'
    
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        product_form = ProductForm()
        return render(request, self.template_name, {
            'products': products,
            'product_form': product_form,
        })

    def post(self, request, *args, **kwargs):
        if 'create_product' in request.POST:
            product_form = ProductForm(request.POST, request.FILES)
            if product_form.is_valid():
                product_form.save()
                messages.success(request, 'Prodotto creato con successo!')
                return redirect('inventory:product_view')
            else:
                for field, errors in product_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
        
        elif 'update_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product_form = ProductForm(request.POST, request.FILES, instance=product)
            if product_form.is_valid():
                product_form.save()
                messages.success(request, 'Prodotto aggiornato con successo!')
                return redirect('inventory:product_view')
            else:
                for field, errors in product_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
        
        elif 'delete_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            messages.success(request, 'Prodotto eliminato con successo!')
            return redirect('inventory:product_view')
        
        products = Product.objects.all()
        return render(request, self.template_name, {
            'products': products,
            'product_form': ProductForm(),
        })



class SaleView(LoginRequiredMixin, View):
    template_name = 'inventory/sale.html'
    
    def get(self, request, *args, **kwargs):
        sales = Sale.objects.all()
        sale_form = SaleForm()
        return render(request, self.template_name, {
            'sales': sales,
            'sale_form': sale_form,
        })

    def post(self, request, *args, **kwargs):
        if 'create_sale' in request.POST:
            sale_form = SaleForm(request.POST)
            if sale_form.is_valid():
                sale_form.save()
                messages.success(request, 'Vendita registrata con successo!')
                return redirect('inventory:sale_view')
            else:
                for field, errors in sale_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
        
        elif 'update_sale' in request.POST:
            sale_id = request.POST.get('sale_id')
            sale = get_object_or_404(Sale, id=sale_id)
            sale_form = SaleForm(request.POST, instance=sale)
            if sale_form.is_valid():
                sale_form.save()
                messages.success(request, 'Vendita aggiornata con successo!')
                return redirect('inventory:sale_view')
            else:
                for field, errors in sale_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
        
        elif 'delete_sale' in request.POST:
            sale_id = request.POST.get('sale_id')
            sale = get_object_or_404(Sale, id=sale_id)
            sale.delete()
            messages.success(request, 'Vendita eliminata con successo!')
            return redirect('inventory:sale_view')
        
        sales = Sale.objects.all()
        return render(request, self.template_name, {
            'sales': sales,
            'sale_form': SaleForm(),
        })
    

class OrderView(LoginRequiredMixin, View):
    template_name = 'inventory/order.html'
    
    def get(self, request, *args, **kwargs):
        orders = Order.objects.all()
        order_form = OrderForm()
        return render(request, self.template_name, {
            'orders': orders,
            'order_form': order_form,
        })

    def post(self, request, *args, **kwargs):
        if 'create_order' in request.POST:
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                order_form.save()
                messages.success(request, 'Ordine creato con successo!')
                return redirect('inventory:order_view')
            else:
                for field, errors in order_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
        
        
        elif 'update_order' in request.POST:
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id)
            order_form = OrderForm(request.POST, instance=order)
            if order_form.is_valid():
                order_form.save()
                messages.success(request, 'Ordine aggiornato con successo!')
                return redirect('inventory:order_view')
            else:
                for field, errors in order_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Errore nel campo '{field}': {error}")
        
        elif 'delete_order' in request.POST:
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id)
            order.delete()
            messages.success(request, 'Ordine eliminato con successo!')
            return redirect('inventory:order_view')
        
        orders = Order.objects.all()
        return render(request, self.template_name, {
            'orders': orders,
            'order_form': OrderForm(),
        })