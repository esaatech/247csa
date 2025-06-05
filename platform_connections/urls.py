from django.urls import path
from . import views

app_name = 'platform_connections'

urlpatterns = [
    # Platform connection management
    path('platforms-connect/', views.platforms_connect, name='platforms_connect'),
    path('platforms-connect/website/', views.website_chat_config, name='website_chat_config'),
    path('platforms-connect/sms/', views.sms_config, name='sms_config'),
    path('platforms-connect/website/disconnect/', views.disconnect_website_chat, name='disconnect_website_chat'),
    path('agent/<uuid:agent_id>/connections/', views.get_agent_connections, name='get_agent_connections'),

    path('agent/<uuid:agent_id>/sessions/', views.chat_session_list, name='chat_session_list'),

    
    # Chat widget endpoints - order matters!
    path('widget/chat/<int:connection_id>/init_session/', views.init_chat_session, name='init_chat_session'),
    path('widget/chat/<int:connection_id>/messages/', views.get_messages, name='get_messages'),
    path('widget/chat/<int:website_id>/<str:token>/container/', views.chat_widget_container, name='chat_widget_container'),
    path('widget/chat/<int:website_id>/<str:token>/', views.chat_widget, name='chat_widget'),
    path('widget/chat/<int:website_id>/<str:token>/update_icon/', views.update_chat_widget_icon, name='update_chat_widget_icon'),
    path('chat/events/<uuid:session_id>/', views.chat_events, name='chat_events'),
    path('end_chat_session/<uuid:session_id>/', views.end_chat_session, name='end_chat_session'),
    path('delete_chat_session/<uuid:session_id>/', views.delete_chat_session, name='delete_chat_session'),
    path('set_handling_mode/<uuid:session_id>/', views.set_handling_mode, name='set_handling_mode'),
]
