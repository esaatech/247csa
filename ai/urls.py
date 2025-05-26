from django.urls import path
from .views import *

app_name = 'ai'

urlpatterns = [
    path('', ai_view, name='ai_view'),
]
    