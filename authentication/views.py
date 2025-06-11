from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import LoginForm
from django.views import View
from django.shortcuts import render
from django.contrib.auth.models import User
from team.models import TeamInvitation, TeamMember
from django.utils import timezone

User = get_user_model()

class CustomLoginView(View):
    template_name = 'authentication/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        # First try authenticating with username
        user = authenticate(username=username_or_email, password=password)
        
        # If username auth fails, try email
        if user is None:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            
            # Handle remember me
            if not remember_me:
                request.session.set_expiry(0)
            
            # Check for pending invitation
            pending_invitation_id = request.session.get('pending_invitation_id')
            if pending_invitation_id:
                del request.session['pending_invitation_id']
                return redirect('team:accept_invitation', invitation_id=pending_invitation_id)
            
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, "Invalid username/email or password.")
        
        return render(request, self.template_name)

class RegisterView(CreateView):
    success_url = reverse_lazy('dashboard:dashboard')
    template_name = 'authentication/register.html'
    form_class = CustomUserCreationForm
    
    def form_valid(self, form):
        # First save the form normally
        response = super().form_valid(form)
        # Get the username and password from the form
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        # Authenticate and login the user
        user = authenticate(username=username, password=password)
        login(self.request, user)
        
        # Check for pending invitation
        pending_invitation_id = self.request.session.get('pending_invitation_id')
        if pending_invitation_id:
            try:
                invitation = get_object_or_404(
                    TeamInvitation,
                    id=pending_invitation_id,
                    is_accepted=False,
                    expires_at__gt=timezone.now()
                )
                
                # Verify email matches
                if invitation.email.lower() == user.email.lower():
                    # Create team membership
                    TeamMember.objects.create(
                        team=invitation.team,
                        user=user,
                        role=invitation.role,
                        invited_by=invitation.invited_by
                    )
                    
                    invitation.is_accepted = True
                    invitation.save()
                    
                    messages.success(self.request, f"You have successfully joined {invitation.team.name}!")
                    return redirect('team:detail', team_id=invitation.team.id)
                else:
                    messages.error(self.request, "The invitation was sent to a different email address.")
            except TeamInvitation.DoesNotExist:
                messages.error(self.request, "The invitation has expired or is no longer valid.")
            finally:
                del self.request.session['pending_invitation_id']
        
        return response

    def get_success_url(self):
        return reverse_lazy('dashboard:dashboard')
        
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

def logout_view(request):
    logout(request)
    return redirect('home:home')