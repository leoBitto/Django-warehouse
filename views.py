# inventory/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Category, Product, Sale, Order
from .forms import CategoryForm, ProductForm, SaleForm, OrderForm

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
                return redirect('inventory:category_view')
        
        elif 'update_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category_form = CategoryForm(request.POST, instance=category)
            if category_form.is_valid():
                category_form.save()
                return redirect('inventory:category_view')
        
        elif 'delete_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            return redirect('inventory:category_view')
        
        categories = Category.objects.all()
        return render(request, self.template_name, {
            'categories': categories,
            'category_form': category_form,
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
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                product_form.save()
                return redirect('inventory:product_view')
        
        elif 'update_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product_form = ProductForm(request.POST, instance=product)
            if product_form.is_valid():
                product_form.save()
                return redirect('inventory:product_view')
        
        elif 'delete_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            return redirect('inventory:product_view')
        
        products = Product.objects.all()
        return render(request, self.template_name, {
            'products': products,
            'product_form': product_form,
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
                return redirect('inventory:sale_view')
        
        elif 'update_sale' in request.POST:
            sale_id = request.POST.get('sale_id')
            sale = get_object_or_404(Sale, id=sale_id)
            sale_form = SaleForm(request.POST, instance=sale)
            if sale_form.is_valid():
                sale_form.save()
                return redirect('inventory:sale_view')
        
        elif 'delete_sale' in request.POST:
            sale_id = request.POST.get('sale_id')
            sale = get_object_or_404(Sale, id=sale_id)
            sale.delete()
            return redirect('inventory:sale_view')
        
        sales = Sale.objects.all()
        return render(request, self.template_name, {
            'sales': sales,
            'sale_form': sale_form,
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
                return redirect('inventory:order_view')
        
        elif 'update_order' in request.POST:
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id)
            order_form = OrderForm(request.POST, instance=order)
            if order_form.is_valid():
                order_form.save()
                return redirect('inventory:order_view')
        
        elif 'delete_order' in request.POST:
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id)
            order.delete()
            return redirect('inventory:order_view')
        
        orders = Order.objects.all()
        return render(request, self.template_name, {
            'orders': orders,
            'order_form': order_form,
        })
