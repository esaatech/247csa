from django.urls import path
from . import views

app_name = 'interaction'

urlpatterns = [
    path('test/', views.test_view, name='test'),
    path('add/', views.add_interaction, name='add_interaction'),
    path('add_slide_out/', views.add_interaction_slide_out, name='add_interaction_slide_out'),
    path('interactions/', views.interactions_list, name='interactions_list'),
    path('interactions_right_slide_out/', views.interactions_right_slide_out, name='interactions_right_slide_out'),
    path('detail/<uuid:interaction_id>/', views.interaction_detail_slide_out, name='interaction_detail_slide_out'),
    path('api/create_interaction/', views.create_interaction, name='create_interaction_api'),
    path('api/update_interaction/<uuid:interaction_id>/', views.update_interaction, name='update_interaction_api'),
    path('api/delete_interaction/<uuid:interaction_id>/', views.delete_interaction, name='delete_interaction_api'),
] 