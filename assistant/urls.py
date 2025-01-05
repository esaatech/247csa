from django.urls import path
from . import views
app_name = 'assistant'
urlpatterns = [
    path('assistant/', views.assistant, name='assistant'),
]   