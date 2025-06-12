from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Ticket

class TicketAccessMixin:
    """Mixin to check ticket access permissions"""
    
    def get_ticket(self):
        ticket_id = self.kwargs.get('pk') or self.kwargs.get('ticket_id')
        return get_object_or_404(Ticket, id=ticket_id)
    
    def dispatch(self, request, *args, **kwargs):
        self.ticket = self.get_ticket()
        
        if not self.ticket.can_view(request.user):
            raise PermissionDenied("You don't have permission to access this ticket")
            
        return super().dispatch(request, *args, **kwargs)

class TicketEditMixin(TicketAccessMixin):
    """Mixin to check ticket edit permissions"""
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            if not self.ticket.can_edit(request.user):
                raise PermissionDenied("You don't have permission to edit this ticket")
        
        return response

class TicketCommentMixin(TicketAccessMixin):
    """Mixin to check ticket comment permissions"""
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        if request.method == 'POST':
            if not self.ticket.can_comment(request.user):
                raise PermissionDenied("You don't have permission to comment on this ticket")
        
        return response 