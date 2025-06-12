from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.db import models
from .models import Ticket, TicketComment, TicketCategory
from .mixins import TicketAccessMixin, TicketEditMixin, TicketCommentMixin
from team.models import Team
from .forms import TicketForm, CategoryForm

# Create your views here.

class TicketDashboardView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets/pages/dashboard.html'
    context_object_name = 'tickets'
    
    def get_queryset(self):
        """Get tickets accessible to the current user with filters"""
        queryset = Ticket.objects.filter(
            teams__members__user=self.request.user,
            teams__members__is_active=True
        ).distinct()
        
        # Apply search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
        
        # Apply filters
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        category = self.request.GET.get('category')
        
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if category:
            queryset = queryset.filter(category_id=category)
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter choices
        context['ticket_statuses'] = self.model.Status.choices
        context['ticket_priorities'] = self.model.Priority.choices
        context['categories'] = TicketCategory.objects.filter(
            teams__members__user=self.request.user,
            teams__members__is_active=True
        ).distinct()
        
        # Add selected filter values
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        context['selected_category'] = self.request.GET.get('category', '')
        
        # Add category form
        context['category_form'] = CategoryForm()
        
        return context

class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/pages/ticket_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Ticket created successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('tickets:detail', kwargs={'pk': self.object.id})

class TicketDetailView(LoginRequiredMixin, TicketAccessMixin, DetailView):
    model = Ticket
    template_name = 'tickets/pages/ticket_detail.html'
    context_object_name = 'ticket'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['can_edit'] = self.object.can_edit(self.request.user)
        context['can_comment'] = self.object.can_comment(self.request.user)
        context['shareable_teams'] = self.object.get_visible_teams(self.request.user)
        return context

class TicketUpdateView(LoginRequiredMixin, TicketEditMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/pages/ticket_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ticket'] = self.object  # Add this to help template know it's an edit
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ticket updated successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('tickets:detail', kwargs={'pk': self.object.id})

class TicketDeleteView(LoginRequiredMixin, TicketEditMixin, DeleteView):
    model = Ticket
    template_name = 'tickets/pages/ticket_confirm_delete.html'
    success_url = reverse_lazy('tickets:dashboard')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Ticket deleted successfully.')
        return super().delete(request, *args, **kwargs)

class TicketCommentCreateView(LoginRequiredMixin, TicketCommentMixin, CreateView):
    model = TicketComment
    template_name = 'tickets/forms/comment_form.html'
    fields = ['content']
    
    def form_valid(self, form):
        form.instance.ticket = self.ticket
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Comment added successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('tickets:detail', kwargs={'pk': self.ticket.id})

class TicketSettingsView(LoginRequiredMixin, TicketAccessMixin, UpdateView):
    model = Ticket
    template_name = 'tickets/pages/ticket_settings.html'
    fields = ['teams']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_teams'] = self.object.get_visible_teams(self.request.user)
        return context

class AddTeamToTicketView(LoginRequiredMixin, TicketEditMixin, View):
    def post(self, request, *args, **kwargs):
        team_id = request.POST.get('team_id')
        if team_id:
            team = get_object_or_404(Team, id=team_id)
            self.ticket.share_with_team(team)
            messages.success(request, f'Added {team.name} to ticket.')
        return HttpResponseRedirect(reverse_lazy('tickets:settings', kwargs={'pk': self.ticket.id}))

class RemoveTeamFromTicketView(LoginRequiredMixin, TicketEditMixin, View):
    def post(self, request, *args, **kwargs):
        team_id = kwargs.get('team_id')
        team = get_object_or_404(Team, id=team_id)
        self.ticket.unshare_with_team(team)
        messages.success(request, f'Removed {team.name} from ticket.')
        return HttpResponseRedirect(reverse_lazy('tickets:settings', kwargs={'pk': self.ticket.id}))

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = TicketCategory
    form_class = CategoryForm
    template_name = 'tickets/components/category_form.html'
    
    def form_valid(self, form):
        # Get the team from the POST data
        team_id = self.request.POST.get('team')
        if team_id:
            category = form.save()
            team = get_object_or_404(Team, id=team_id)
            category.teams.add(team)
            messages.success(self.request, 'Category created successfully.')
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'category': {
                        'id': category.id,
                        'name': category.name
                    }
                })
        return redirect('tickets:dashboard')
