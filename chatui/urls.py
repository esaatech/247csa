from django.urls import path
from . import views

app_name = 'chatui'

urlpatterns = [
    path('chat/<uuid:session_id>/', views.chat_window, name='chat_window'),
    path('chat/<uuid:session_id>/send/', views.send_message, name='send_message'),
]   