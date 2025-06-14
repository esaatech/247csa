from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

class CRMAccessMixin:
    """Base mixin for CRM object access control"""
    def get_object(self):
        obj_id = self.kwargs.get('pk')
        return get_object_or_404(self.model, id=obj_id)
    
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.can_view(request.user):
            raise PermissionDenied("You don't have permission to access this object")
        return super().dispatch(request, *args, **kwargs)

class CRMEditMixin(CRMAccessMixin):
    """Mixin for CRM object edit permissions"""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            if not self.object.can_edit(request.user):
                raise PermissionDenied("You don't have permission to edit this object")
        return response 