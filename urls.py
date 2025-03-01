from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Product Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<int:category_id>/', views.CategoryDetailView.as_view(), name='category_detail'),
]