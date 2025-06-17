from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_nested import routers

app_name = 'csa'

router = DefaultRouter()
router.register(r'csa', views.CSAViewSet, basename='csa')

urlpatterns = [
    path('', include(router.urls)),
    path('list/', views.csa_list, name='list'),
    path('create/', views.csa_create, name='create'),
    path('<uuid:pk>/', views.csa_detail, name='detail'),
    path('<uuid:pk>/edit/', views.csa_edit, name='edit'),
    path('crm-connect/', views.crm_connect, name='crm_connect'),
    path('<uuid:pk>/faqs/', views.csa_faqs_api, name='csa_faqs_api'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('welcome-message/', views.welcome_message, name='welcome_message'),
]
