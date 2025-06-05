from django.urls import path
from . import views

app_name = 'faq_management'

urlpatterns = [
    path('test/', views.test_faq_system, name='test_faq_system'),
    path('template/', views.faq_template, name='faq_template'),
    path('faq/save/', views.save_faqs, name='save_faqs'),
    path('faq/<int:faq_id>/', views.get_faq, name='get_faq'),
    path('faq/<int:faq_id>/delete/', views.delete_faq, name='delete_faq'),
    path('faq/group/<str:faqid>/', views.get_faqs_by_faqid, name='get_faqs_by_faqid'),
    path('faq/<int:faq_id>/update/', views.update_faq, name='update_faq'),
    path('faq/create/', views.create_faq, name='create_faq'),
    path('faq/right-panel/', views.faq_template_right_panel, name='faq_template_right_panel'),
    path('faq/chat-block/', views.faq_in_chat_widget, name='faq_in_chat_widget'),
    path('faq/website/', views.website_faqs, name='website_faqs'),
] 