from django.views.generic import View
from django.shortcuts import render, redirect
from .models import Item
from .forms import ItemForm

class InventoryView(View):
    def get(self, request, *args, **kwargs):
        item_id = kwargs.get('pk')
        if item_id:
            item = Item.objects.get(pk=item_id)
            return render(request, 'inventory/item_detail.html', {'item': item})
        else:
            items = Item.objects.all()
            return render(request, 'inventory/item_list.html', {'items': items})

    def post(self, request, *args, **kwargs):
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
        else:
            return render(request, 'inventory/item_form.html', {'form': form})

    def put(self, request, *args, **kwargs):
        item_id = kwargs.get('pk')
        item = Item.objects.get(pk=item_id)
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
        else:
            return render(request, 'inventory/item_form.html', {'form': form})

    def delete(self, request, *args, **kwargs):
        item_id = kwargs.get('pk')
        item = Item.objects.get(pk=item_id)
        item.delete()
        return redirect('inventory_list')
