from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from warehouse.models import Product, ProductCategory, ProductSupplierCode
from warehouse.forms import ProductForm, ProductCategoryForm, ProductSupplierCodeForm

class ProductListView(View):
    template_name = 'warehouse/products.html'

    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        form = ProductForm()
        return render(request, self.template_name, {'products': products, 'form': form})

    def post(self, request, *args, **kwargs):
        if 'delete_object' in request.POST:
            product = get_object_or_404(Product, id=request.POST.get('delete_object'))
            product.delete()
            return redirect('warehouse:product_list')

        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('warehouse:product_list')

        products = Product.objects.all()
        return render(request, self.template_name, {'products': products, 'form': form})

class ProductDetailView(View):
    template_name = 'warehouse/product_detail.html'

    def get(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(instance=product)
        supplier_code_form = ProductSupplierCodeForm()
        supplier_codes = ProductSupplierCode.objects.filter(product=product)
        return render(request, self.template_name, {
            'product': product, 
            'form': form, 
            'supplier_code_form': supplier_code_form, 
            'supplier_codes': supplier_codes
        })

    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)

        if 'update_product' in request.POST:
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                return redirect('warehouse:product_list')

        elif 'delete_product' in request.POST:
            product.delete()
            return redirect('warehouse:product_list')

        elif 'add_supplier_code' in request.POST:
            supplier_code_form = ProductSupplierCodeForm(request.POST)
            if supplier_code_form.is_valid():
                supplier_code = supplier_code_form.save(commit=False)
                supplier_code.product = product
                supplier_code.save()
                return redirect('warehouse:product_detail', product_id=product.id)

        supplier_code_form = ProductSupplierCodeForm()
        supplier_codes = ProductSupplierCode.objects.filter(product=product)
        return render(request, self.template_name, {
            'product': product, 
            'form': form, 
            'supplier_code_form': supplier_code_form, 
            'supplier_codes': supplier_codes
        })

class CategoryListView(View):
    template_name = 'warehouse/categories.html'

    def get(self, request, *args, **kwargs):
        categories = ProductCategory.objects.all()
        form = ProductCategoryForm()
        return render(request, self.template_name, {'categories': categories, 'form': form})

    def post(self, request, *args, **kwargs):
        if 'delete_object' in request.POST:
            category = get_object_or_404(ProductCategory, id=request.POST.get('delete_object'))
            category.delete()
            return redirect('warehouse:category_list')

        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('warehouse:category_list')

        categories = ProductCategory.objects.all()
        return render(request, self.template_name, {'categories': categories, 'form': form})

class CategoryDetailView(View):
    template_name = 'warehouse/category_detail.html'

    def get(self, request, category_id, *args, **kwargs):
        category = get_object_or_404(ProductCategory, id=category_id)
        form = ProductCategoryForm(instance=category)
        return render(request, self.template_name, {'category': category, 'form': form})

    def post(self, request, category_id, *args, **kwargs):
        category = get_object_or_404(ProductCategory, id=category_id)

        if 'update_category' in request.POST:
            form = ProductCategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                return redirect('warehouse:category_list')

        elif 'delete_category' in request.POST:
            category.delete()
            return redirect('warehouse:category_list')

        return render(request, self.template_name, {'category': category, 'form': form})
