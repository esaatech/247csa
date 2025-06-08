from django.urls import path
from . import views

app_name = 'task'

urlpatterns = [
    path('test/', views.test_view, name='test'),
    path('add/', views.add_task, name='add_task'),
    path('add_slide_out/', views.add_task_slide_out, name='add_task_slide_out'),
    path('tasks/', views.tasks_list, name='tasks_list'),
    path('tasks_right_slide_out/', views.tasks_right_slide_out, name='tasks_right_slide_out'),
    path('api/create_task/', views.create_task, name='create_task_api'),
    path('api/update_task/<uuid:task_id>/', views.update_task, name='update_task_api'),
    path('api/delete_task/<uuid:task_id>/', views.delete_task, name='delete_task_api'),
] 