from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import EmailViewSet, WhatsAppMessageViewSet
app_name = 'assistant'

router = DefaultRouter()
router.register(r'emails', EmailViewSet, basename='email')
router.register(r'whatsapp-messages', WhatsAppMessageViewSet, basename='whatsappmessage')



urlpatterns = [    
    path("facebook_messenger_webhook/", views.facebook_messenger_webhook, name="facebook_messenger_webhook"),
    path('assistant/', views.assistant, name='assistant'),
     path('api/', include(router.urls)),
    path('api/whatsapp/send/', views.send_whatsapp_message, name='send-whatsapp'),
    path("facebook_messenger/", views.facebook_messenger, name="facebook_messenger"),
]   
