from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    # Team Management
    path('', views.team_list, name='list'),
    path('create/', views.create_team, name='create'),
    path('<uuid:team_id>/', views.team_detail, name='detail'),
    path('<uuid:team_id>/edit/', views.edit_team, name='edit'),
    path('<uuid:team_id>/delete/', views.delete_team, name='delete'),
    
    # Team Members
    path('<uuid:team_id>/members/add/', views.add_member, name='add_member'),
    path('<uuid:team_id>/members/<uuid:member_id>/remove/', views.remove_member, name='remove_member'),
    path('<uuid:team_id>/members/<uuid:member_id>/role/', views.change_member_role, name='change_role'),
    
    # Invitations
    path('<uuid:team_id>/invite/', views.send_invitation, name='send_invitation'),
    path('invitation/<uuid:invitation_id>/accept/', views.accept_invitation, name='accept_invitation'),
    path('invitation/<uuid:invitation_id>/decline/', views.decline_invitation, name='decline_invitation'),
    path('<uuid:team_id>/invitation/<uuid:invitation_id>/cancel/', views.cancel_invitation, name='cancel_invitation'),
] 