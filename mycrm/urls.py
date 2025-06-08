from django.urls import path
from . import views

app_name = 'mycrm'

urlpatterns = [
    # Main views
    path('', views.dashboard, name='dashboard'),

    path('test', views.test_view, name='test_view'),
    path('add/', views.add_customer, name='add_customer'),
    path('customers/', views.customers_list, name='customers_list'),
    
    # MCP API endpoints
    path('mcp/create_customer/', views.create_customer, name='create_customer'),
    path('mcp/get_customer/', views.get_customer, name='get_customer'),
    path('mcp/update_customer/', views.update_customer, name='update_customer'),
    path('mcp/delete_customer/', views.delete_customer, name='delete_customer'),
    path('mcp/log_interaction/', views.log_interaction, name='log_interaction'),
    path('mcp/create_task/', views.create_task, name='create_task'),
    path('mcp/get_tasks/', views.get_tasks, name='get_tasks'),
] 