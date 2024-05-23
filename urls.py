from django.urls import path
from .views import InventoryView

urlpatterns = [
    path('inventory/', InventoryView.as_view(), name='inventory_list'),
    path('inventory/<int:pk>/', InventoryView.as_view(), name='inventory_detail'),
]
