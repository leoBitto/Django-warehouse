from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from warehouse.models.base import *
from warehouse.forms import *
from billing.models.base import InvoiceLine, Invoice
from django.contrib import messages
from django import forms

class ProductListView(View):
    template_name = 'warehouse/product_list.html'

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
        
        # Inizializza il form con il prodotto preselezionato e nasconde il campo
        supplier_code_form = ProductAliasForm(initial={'product': product})
        supplier_code_form.fields['product'].widget = forms.HiddenInput()
        
        image_form = ProductImageForm()

        supplier_codes = ProductAlias.objects.filter(product=product)
        product_images = ProductImage.objects.filter(product=product)

        # Ottieni tutte le InvoiceLine per il prodotto
        invoice_lines = InvoiceLine.objects.filter(product=product)

        # Dividi in acquisti e vendite
        purchases = [line for line in invoice_lines if line.invoice.invoice_type == 'IN']
        sales = [line for line in invoice_lines if line.invoice.invoice_type == 'OUT']

        return render(request, self.template_name, {
            'product': product,
            'form': form,
            'supplier_code_form': supplier_code_form,
            'image_form': image_form,
            'supplier_codes': supplier_codes,
            'product_images': product_images,
            'purchases': purchases,
            'sales': sales,
        })

    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)

        if 'update_product' in request.POST:
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, "Prodotto aggiornato con successo!")
                return redirect('warehouse:product_list')
            else:
                messages.error(request, "Errore nell'aggiornamento del prodotto.")

        elif 'delete_product' in request.POST:
            try:
                product.delete()
                messages.success(request, "Prodotto eliminato con successo!")
                return redirect('warehouse:product_list')
            except Exception as e:
                messages.error(request, f"Errore durante l'eliminazione del prodotto: {str(e)}")

        elif 'add_supplier_code' in request.POST:
            supplier_code_form = ProductAliasForm(request.POST)
            if supplier_code_form.is_valid():
                supplier_code = supplier_code_form.save(commit=False)
                supplier_code.product = product  # Assicurati che il prodotto sia impostato
                supplier_code.save()
                messages.success(request, "Aggiunto codice con successo!")
                return redirect('warehouse:product_detail', product_id=product.id)
            else:
                messages.error(request, "Errore nel caricamento del codice.")
        
        elif 'delete_supplier_code' in request.POST:
            supplier_code_id = request.POST.get('supplier_code_id')
            if supplier_code_id:
                supplier_code = get_object_or_404(ProductAlias, id=supplier_code_id, product=product)
                supplier_code.delete()
                messages.success(request, "Codice fornitore eliminato con successo!")
                return redirect('warehouse:product_detail', product_id=product.id)

        elif 'add_image' in request.POST:
            image_form = ProductImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                image = image_form.save(commit=False)
                image.product = product
                try:
                    image.save()
                    messages.success(request, "Immagine caricata con successo!")
                except Exception as e:
                    print("Errore durante il salvataggio:", str(e))
                    messages.error(request, f"Errore durante il salvataggio: {str(e)}")
                return redirect('warehouse:product_detail', product_id=product.id)
            else:
                messages.error(request, f"Errore nel form immagine: {image_form.errors}")

        elif 'delete_image' in request.POST:
            image_id = request.POST.get('image_id')
            if image_id:
                try:
                    image = get_object_or_404(ProductImage, id=image_id, product=product)
                    image.delete()
                    messages.success(request, "Immagine eliminata con successo!")
                except Exception as e:
                    messages.error(request, f"Errore durante l'eliminazione dell'immagine: {str(e)}")
                return redirect('warehouse:product_detail', product_id=product.id)

        # Prepara i dati per il rendering della pagina
        form = ProductForm(instance=product)
        
        # Inizializza il form con il prodotto preselezionato e nasconde il campo
        supplier_code_form = ProductAliasForm(initial={'product': product})
        supplier_code_form.fields['product'].widget = forms.HiddenInput()
        
        image_form = ProductImageForm()
        supplier_codes = ProductAlias.objects.filter(product=product)
        product_images = ProductImage.objects.filter(product=product)

        # Ottieni tutte le InvoiceLine per il prodotto
        invoice_lines = InvoiceLine.objects.filter(product=product)

        # Dividi in acquisti e vendite
        purchases = [line for line in invoice_lines if line.invoice.invoice_type == 'IN']
        sales = [line for line in invoice_lines if line.invoice.invoice_type == 'OUT']

        return render(request, self.template_name, {
            'product': product,
            'form': form,
            'supplier_code_form': supplier_code_form,
            'image_form': image_form,
            'supplier_codes': supplier_codes,
            'product_images': product_images,
            'purchases': purchases,
            'sales': sales,
        })
        
class ProductImageDetailView(View):
    template_name = "warehouse/product_image_detail.html"

    def get(self, request, image_id, *args, **kwargs):
        image = get_object_or_404(ProductImage, id=image_id)
        form = ProductImageForm(instance=image)

        return render(request, self.template_name, {
            "image": image,
            "form": form
        })

    def post(self, request, image_id, *args, **kwargs):
        image = get_object_or_404(ProductImage, id=image_id)

        if "delete_image" in request.POST:
            image.delete()
            return redirect("product_detail", product_id=image.product.id)

        form = ProductImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect("warehouse:product_image_detail", image_id=image.id)

        return render(request, self.template_name, {
            "image": image,
            "form": form
        })



class CategoryListView(View):
    template_name = 'warehouse/category_list.html'

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
        products = category.products.all()  # Recuperiamo i prodotti associati
        form = ProductCategoryForm(instance=category)
        return render(request, self.template_name, {
            'category': category,
            'products': products,
            'form': form
        })

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

        products = category.products.all()  # Assicuriamoci di includere sempre i prodotti
        return render(request, self.template_name, {
            'category': category,
            'products': products,
            'form': form
        })
