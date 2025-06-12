from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    # Dashboard
    path('', views.TicketDashboardView.as_view(), name='dashboard'),
    
    # Ticket CRUD
    path('create/', views.TicketCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.TicketDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.TicketUpdateView.as_view(), name='edit'),
    path('<uuid:pk>/delete/', views.TicketDeleteView.as_view(), name='delete'),
    path('<uuid:pk>/settings/', views.TicketSettingsView.as_view(), name='settings'),
    
    # Comments
    path('<uuid:ticket_id>/comment/', views.TicketCommentCreateView.as_view(), name='add_comment'),
    
    # Team Management
    path('<uuid:pk>/teams/add/', views.AddTeamToTicketView.as_view(), name='add_team'),
    path('<uuid:pk>/teams/<uuid:team_id>/remove/', views.RemoveTeamFromTicketView.as_view(), name='remove_team'),
    
    # Categories
    path('categories/create/', views.CategoryCreateView.as_view(), name='create_category'),
] 