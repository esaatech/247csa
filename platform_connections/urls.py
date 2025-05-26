from django.urls import path
from . import views

app_name = 'platform_connections'

urlpatterns = [
    path('platforms-connect/', views.platforms_connect, name='platforms_connect'),
    path('platforms-connect/website/', views.website_chat_config, name='website_chat_config'),
    path('platforms-connect/sms/', views.sms_config, name='sms_config'),
    path('platforms-connect/website/disconnect/', views.disconnect_website_chat, name='disconnect_website_chat'),
    path('agent/<uuid:agent_id>/connections/', views.get_agent_connections, name='get_agent_connections'),
]
