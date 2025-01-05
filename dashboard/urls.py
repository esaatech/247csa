from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('assistants/', views.assistant_list, name='assistants'),
    path('assistants/create/', views.create_assistant, name='create_assistant'),
    path('integrations/', views.integration_list, name='integrations'),
] 