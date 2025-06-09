from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from mycrm.models import Customer
from csa.models import CSA
from platform_connections.models import ChatSession


@login_required
def dashboard(request):
    # Get current time and last week
    now = timezone.now()
    last_week = now - timedelta(days=7)
    
    # CRM Context - Filter by current user
    crm_context = {
        'total_customers': Customer.objects.filter(created_by=request.user).count(),
        'new_customers': Customer.objects.filter(created_by=request.user, created_at__gte=last_week).count(),
        'recent_customers': Customer.objects.filter(created_by=request.user).order_by('-created_at')[:5],
        'followup_tasks': Customer.objects.filter(
            created_by=request.user,
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
    
    # Combine all context
    context = {
        **crm_context,
        **agents_context,
        'user': request.user,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

def create_csa(request):
    return render(request, 'dashboard/create_csa.html')

