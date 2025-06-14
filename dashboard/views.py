from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from mycrm.models import Customer
from csa.models import CSA
from platform_connections.models import ChatSession
from settings.models import UserPreference
from task.models import Task
from tickets.models import Ticket


def get_priority_weight(priority):
    """Helper function to convert priority to numeric weight for sorting"""
    priority_weights = {'high': 0, 'medium': 1, 'low': 2}
    return priority_weights.get(priority, 3)


@login_required
def dashboard(request):
    # Get current time and last week
    now = timezone.now()
    today = now.date()
    last_week = now - timedelta(days=7)
    
    # Get or create user preferences
    user_preferences, created = UserPreference.objects.get_or_create(user=request.user)
    
    # Get all customers for the current user's teams (team-based access)
    user_teams_customers = Customer.objects.filter(teams__members__user=request.user, teams__members__is_active=True).distinct()
    
    # Create a mapping of task_uuid to customer_id
    task_uuid_to_customer = {
        str(customer.task_uuid): customer.id 
        for customer in user_teams_customers
    }
    
    # Get all task_uuids for the user's team customers
    customer_task_uuids = user_teams_customers.values_list('task_uuid', flat=True)
    
    # Get tasks for the user's team customers
    all_tasks = Task.objects.filter(task_uuid__in=customer_task_uuids)
    
    # Create task dictionaries with customer IDs
    task_dicts = []
    for task in all_tasks:
        customer_id = task_uuid_to_customer.get(str(task.task_uuid))
        if customer_id:
            task_dict = {
                'id': task.id,
                'title': task.title,
                'due_date': task.due_date,
                'is_completed': task.is_completed,
                'customer_id': customer_id,
                'priority': task.priority,
                'is_due_today': task.due_date.date() == today if task.due_date else False,
                'is_overdue': task.due_date.date() < today if task.due_date else False,
                'priority_weight': get_priority_weight(task.priority)
            }
            task_dicts.append(task_dict)
    
    # Group tasks by date status and priority
    due_today_tasks = []
    overdue_tasks = []
    future_tasks = []

    for task in sorted(task_dicts, key=lambda x: (x['priority_weight'], x['due_date'] or timezone.now())):
        if task['is_due_today']:
            due_today_tasks.append(task)
        elif task['is_overdue']:
            overdue_tasks.append(task)
        else:
            future_tasks.append(task)
    
    # Tasks Context
    tasks_context = {
        'total_tasks': all_tasks.count(),
        'due_today': len(due_today_tasks),
        'due_today_tasks': due_today_tasks,
        'overdue_tasks': overdue_tasks,
        'future_tasks': future_tasks,
    }
    
    # CRM Context (team-based)
    crm_context = {
        'total_customers': user_teams_customers.count(),
        'new_customers': user_teams_customers.filter(created_at__gte=last_week).count(),
        'recent_customers': user_teams_customers.order_by('-created_at')[:5],
        'followup_tasks': user_teams_customers.filter(
            tasks__due_date__lt=now,
            tasks__is_completed=False
        ).distinct()[:3]
    }
    
    # Get user's CSAs
    user_csas = CSA.objects.filter(user=request.user)
    
    # Get active chat sessions for user's CSAs
    active_sessions = ChatSession.objects.filter(
        agent_id__in=user_csas.values_list('id', flat=True),
        is_active=True
    )
    
    # Count CSAs by handling mode
    ai_agents = user_csas.filter(default_handling_mode='ai').count()
    human_agents = user_csas.filter(default_handling_mode='human').count()
    
    # Agents Context
    agents_context = {
        'total_agents': user_csas.count(),
        'active_agents': user_csas.filter(status='ready').count(),
        'online_agents': user_csas.filter(status='ready').order_by('-updated_at')[:5].select_related('user'),
        'ai_agents': ai_agents,
        'human_agents': human_agents,
        'active_chats': active_sessions.count(),
        'avg_response_time': 5,  # Placeholder - will implement when we add response tracking
        'satisfaction_rate': 95,  # Placeholder - will implement when we add feedback system
        'resolved_tickets': active_sessions.filter(is_active=False).count()  # Using completed sessions as proxy
    }
    
    # Get tickets accessible to the user
    user_tickets = Ticket.objects.filter(
        teams__members__user=request.user,
        teams__members__is_active=True
    ).distinct()
    
    # Tickets Context
    tickets_context = {
        'total_tickets': user_tickets.count(),
        'urgent_tickets': user_tickets.filter(priority=Ticket.Priority.URGENT).count(),
        'recent_tickets': user_tickets.order_by('-created_at')[:4],
        'urgent_ticket_list': user_tickets.filter(
            priority=Ticket.Priority.URGENT,
            status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS]
        ).order_by('-created_at')[:3]
    }
    
    # Settings Context
    settings_context = {
        'user_preferences': user_preferences,
    }
    
    # Combine all context
    context = {
        **crm_context,
        **agents_context,
        **settings_context,
        **tasks_context,
        **tickets_context,
        'user': request.user,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

def create_csa(request):
    return render(request, 'dashboard/create_csa.html')

