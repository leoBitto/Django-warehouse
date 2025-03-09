import pandas as pd
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from warehouse.forms import InventoryUploadForm
from warehouse.models.base import *

class InventoryUploadView(View):
    template_name = "warehouse/inventory_upload.html"
    
    def get(self, request):
        form = InventoryUploadForm()
        return render(request, self.template_name, {"form": form})
    
    def post(self, request):
        form = InventoryUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_path = fs.path(filename)
            
            try:
                df = pd.read_excel(file_path)
                if not {"product_name", "quantity"}.issubset(df.columns):
                    messages.error(request, "Il file Excel deve contenere le colonne 'product_name' e 'quantity'.")
                    return redirect("warehouse:inventory_upload")
                
                for _, row in df.iterrows():
                    product_name = row["product_name"].strip()
                    quantity = int(row["quantity"])
                    
                    product, created = Product.objects.get_or_create(name=product_name)
                    product.update_stock(quantity)  # Aggiorniamo lo stock
                    product.save()
                
                messages.success(request, "Inventario aggiornato con successo!")
                return redirect("warehouse:product_list")
            except Exception as e:
                messages.error(request, f"Errore durante l'elaborazione del file: {str(e)}")
                return redirect("warehouse:inventory_upload")
        
        return render(request, self.template_name, {"form": form})
