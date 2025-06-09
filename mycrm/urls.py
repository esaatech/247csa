from django.urls import path
from . import views

app_name = 'mycrm'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Customer CRUD
    path('customer/add/', views.add_customer, name='add_customer'),
    path('customer/create/', views.create_customer, name='create_customer'),
    path('customer/<int:customer_id>/update/', views.update_customer, name='update_customer'),
    path('customer/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),
    
    # Customer Detail
    path('customer/<int:customer_id>/detail/', views.get_customer_detail, name='get_customer_detail'),
    
    # Search
    path('search/', views.search_customers, name='search_customers'),
] 