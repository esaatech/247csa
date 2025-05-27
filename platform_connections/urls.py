from django.urls import path
from . import views

app_name = 'platform_connections'

urlpatterns = [
    path('platforms-connect/', views.platforms_connect, name='platforms_connect'),
    path('platforms-connect/website/', views.website_chat_config, name='website_chat_config'),
    path('platforms-connect/sms/', views.sms_config, name='sms_config'),
    path('platforms-connect/website/disconnect/', views.disconnect_website_chat, name='disconnect_website_chat'),
    path('agent/<uuid:agent_id>/connections/', views.get_agent_connections, name='get_agent_connections'),
    path('widget/chat/<int:website_id>/<str:token>/', views.chat_widget, name='chat_widget'),
    path('widget/chat/<int:connection_id>/send/', views.send_message, name='send_message'),
    path('widget/chat/<int:connection_id>/messages/', views.get_messages, name='get_messages'),
    path('widget/chat/<int:connection_id>/send/', views.send_message, name='send_message'),
    path('widget/chat/<int:website_id>/<str:token>/', views.chat_widget, name='chat_widget'),
]
