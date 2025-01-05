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
    path('assistant/', views.assistant, name='assistant'),
     path('api/', include(router.urls)),
]   