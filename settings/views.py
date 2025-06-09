from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

@login_required
def settings_dashboard(request):
    context = {
        'active_section': 'dashboard',
        'page_title': 'Settings Dashboard'
    }
    return render(request, 'settings/dashboard.html', context)

@login_required
def profile_settings(request):
    context = {
        'active_section': 'profile',
        'page_title': 'Profile Settings'
    }
    return render(request, 'settings/profile.html', context)

@login_required
def notification_settings(request):
    context = {
        'active_section': 'notifications',
        'page_title': 'Notification Preferences'
    }
    return render(request, 'settings/notifications.html', context)

@login_required
def integration_settings(request):
    context = {
        'active_section': 'integrations',
        'page_title': 'Platform Integrations'
    }
    return render(request, 'settings/integrations.html', context)

@login_required
def billing_settings(request):
    context = {
        'active_section': 'billing',
        'page_title': 'Billing & Subscription'
    }
    return render(request, 'settings/billing.html', context)

@login_required
def security_settings(request):
    context = {
        'active_section': 'security',
        'page_title': 'Security Settings'
    }
    return render(request, 'settings/security.html', context)
