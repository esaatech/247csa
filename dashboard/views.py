from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assistant
from .models import Assistant
from csa.models import CSA


@login_required(login_url='/login/')
def dashboard(request):
    # Show welcome message if no id is passed
    return render(request, 'dashboard/dashboard.html')

def create_csa(request):
    return render(request, 'dashboard/create_csa.html')

