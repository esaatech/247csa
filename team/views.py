from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
from .models import Team, TeamMember, TeamInvitation, User
from django.contrib import messages
from email_utility.services.notification_service import NotificationService
from .forms import TeamForm
from authentication.forms import CustomUserCreationForm
from django.contrib.auth import login

@login_required
def team_list(request):
    """List all teams the user is a member of."""
    user_teams = TeamMember.objects.filter(user=request.user, is_active=True).select_related('team')
    return render(request, 'team/list.html', {
        'user_teams': user_teams
    })

@login_required
def create_team(request):
    """Create a new team."""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            team = Team.objects.create(name=name, owner=request.user)
            # Add creator as team owner
            TeamMember.objects.create(
                team=team,
                user=request.user,
                role=TeamMember.Roles.OWNER
            )
            return redirect('team:detail', team_id=team.id)
    return render(request, 'team/create.html')

@login_required
def team_detail(request, team_id):
    """View team details."""
    team = get_object_or_404(Team, id=team_id)
    member = get_object_or_404(TeamMember, team=team, user=request.user, is_active=True)
    team_members = TeamMember.objects.filter(team=team, is_active=True).select_related('user')
    
    # Get pending invitations
    pending_invitations = TeamInvitation.objects.filter(
        team=team,
        is_accepted=False,
        expires_at__gt=timezone.now()
    ).order_by('-created_at')
    
    # Clear any existing messages to prevent them from persisting
    storage = messages.get_messages(request)
    storage.used = True
    
    return render(request, 'team/detail.html', {
        'team': team,
        'member': member,
        'team_members': team_members,
        'can_manage_team': member.is_admin or member.is_owner,
        'pending_invitations': pending_invitations
    })

@login_required
def edit_team(request, team_id):
    """Edit team details."""
    team = get_object_or_404(Team, id=team_id)
    member = get_object_or_404(TeamMember, team=team, user=request.user, is_active=True)
    
    if not member.is_admin:
        return HttpResponseForbidden("You don't have permission to edit this team.")
    
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, "Team settings updated successfully.")
            return redirect('team:detail', team_id=team.id)
    else:
        form = TeamForm(instance=team)
    
    return render(request, 'team/edit.html', {
        'team': team,
        'form': form
    })

@login_required
def delete_team(request, team_id):
    """Delete a team."""
    team = get_object_or_404(Team, id=team_id)
    member = get_object_or_404(TeamMember, team=team, user=request.user, is_active=True)
    
    if not member.is_owner:
        return HttpResponseForbidden("Only the team owner can delete the team.")
    
    if request.method == 'POST':
        team.delete()
        return redirect('team:list')
    
    return render(request, 'team/delete_confirm.html', {'team': team})

@login_required
def add_member(request, team_id):
    """Add a new team member directly."""
    team = get_object_or_404(Team, id=team_id)
    member = get_object_or_404(TeamMember, team=team, user=request.user, is_active=True)
    
    if not member.is_admin:
        return HttpResponseForbidden("You don't have permission to add members.")
    
    if request.method == 'POST':
        email = request.POST.get('email')
        role = request.POST.get('role', TeamMember.Roles.MEMBER)
        
        if email and role in dict(TeamMember.Roles.choices):
            # Check for existing pending invitation
            existing_invitation = TeamInvitation.objects.filter(
                team=team,
                email=email,
                is_accepted=False,
                expires_at__gt=timezone.now()
            ).first()
            
            if existing_invitation:
                messages.warning(request, f"An invitation for {email} is already pending.")
                return redirect('team:detail', team_id=team.id)

            # Check if user already exists
            existing_user = User.objects.filter(email=email).first()
            
            if existing_user:
                # Check if user is already in this team
                existing_member = TeamMember.objects.filter(user=existing_user, team=team, is_active=True).first()
                if existing_member:
                    messages.warning(request, f"{email} is already a member of this team.")
                    return redirect('team:detail', team_id=team.id)
                
                # Check if user is in another team
                other_team_member = TeamMember.objects.filter(user=existing_user, is_active=True).first()
                if other_team_member:
                    messages.error(request, f"{email} is already a member of another team. Users can only be in one team.")
                    return redirect('team:detail', team_id=team.id)
            
            try:
                # Create invitation that expires in 7 days
                expires_at = timezone.now() + timedelta(days=7)
                invitation = TeamInvitation.objects.create(
                    team=team,
                    email=email,
                    role=role,
                    invited_by=request.user,
                    expires_at=expires_at
                )
                
                # Send invitation email using the notification service
                if NotificationService.send_team_invitation(invitation):
                    messages.success(request, f"Invitation sent to {email}")
                else:
                    messages.warning(request, f"Invitation created but email could not be sent to {email}")
                    
            except Exception as e:
                messages.error(request, f"Failed to send invitation: {str(e)}")
                
            return redirect('team:detail', team_id=team.id)
    
    return render(request, 'team/add_member.html', {'team': team})

@login_required
def remove_member(request, team_id, member_id):
    """Remove a team member."""
    team = get_object_or_404(Team, id=team_id)
    user_member = get_object_or_404(TeamMember, team=team, user=request.user, is_active=True)
    member_to_remove = get_object_or_404(TeamMember, id=member_id, team=team)
    
    if not user_member.is_admin or member_to_remove.is_owner:
        return HttpResponseForbidden("You don't have permission to remove this member.")
    
    if request.method == 'POST':
        # Store user email for notification
        removed_user_email = member_to_remove.user.email
        removed_user_name = member_to_remove.user.get_full_name() or removed_user_email
        
        # Actually delete the team membership instead of just marking inactive
        member_to_remove.delete()
        
        # Send notification to the removed user
        try:
            NotificationService.send_team_removal_notification(
                user_email=removed_user_email,
                team_name=team.name,
                removed_by=request.user.get_full_name() or request.user.email
            )
            messages.success(
                request, 
                f"{removed_user_name} has been removed from the team. They have been notified by email."
            )
        except Exception as e:
            messages.success(
                request, 
                f"{removed_user_name} has been removed from the team. However, we couldn't send them a notification email."
            )
        
        return redirect('team:detail', team_id=team.id)
    
    return render(request, 'team/remove_member_confirm.html', {
        'team': team,
        'member': member_to_remove
    })

@login_required
def change_member_role(request, team_id, member_id):
    """Change a team member's role."""
    if request.method != 'POST':
        return HttpResponseForbidden("Method not allowed")
    
    team = get_object_or_404(Team, id=team_id)
    user_member = get_object_or_404(TeamMember, team=team, user=request.user, is_active=True)
    member_to_change = get_object_or_404(TeamMember, id=member_id, team=team, is_active=True)
    
    if not user_member.is_owner:
        messages.error(request, "Only team owners can change member roles.")
        return redirect('team:detail', team_id=team.id)
    
    new_role = request.POST.get('role')
    if new_role not in dict(TeamMember.Roles.choices):
        messages.error(request, "Invalid role selected.")
        return redirect('team:detail', team_id=team.id)
    
    # Prevent changing the owner's role
    if member_to_change.is_owner:
        messages.error(request, "Cannot change the owner's role.")
        return redirect('team:detail', team_id=team.id)
    
    member_to_change.role = new_role
    member_to_change.save()
    
    messages.success(request, f"Successfully changed {member_to_change.user.email}'s role to {new_role}.")
    return redirect('team:detail', team_id=team.id)

@login_required
def send_invitation(request, team_id):
    print("send_invitation")
    """Send a team invitation."""
    if request.method == "POST":
        email = request.POST.get('email')
        team = get_object_or_404(Team, id=team_id)
        
        # Create the invitation
        invitation = TeamInvitation.objects.create(
            team=team,
            email=email,
            invited_by=request.user
        )
        
        # Send the email (you'll need to implement this)
        # send_invitation_email(invitation)
        
        # Add a success message
        messages.success(request, f"Invitation sent to {email}")
        
        # Redirect back to the team detail page
        return redirect('team:detail', team_id=team_id)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def accept_invitation(request, invitation_id):
    """Accept a team invitation."""
    invitation = get_object_or_404(
        TeamInvitation,
        id=invitation_id,
        is_accepted=False,
        expires_at__gt=timezone.now()
    )
    
    # If user is not logged in, redirect to team-specific registration
    if not request.user.is_authenticated:
        return redirect('team:invited_register', invitation_id=invitation_id)
    
    # Check if the invitation matches the user's email
    if invitation.email.lower() != request.user.email.lower():
        messages.error(request, "This invitation was sent to a different email address.")
        return redirect('home:home')
    
    # Create team membership
    TeamMember.objects.create(
        team=invitation.team,
        user=request.user,
        role=invitation.role,
        invited_by=invitation.invited_by
    )
    
    invitation.is_accepted = True
    invitation.save()
    
    messages.success(request, f"You have successfully joined {invitation.team.name}!")
    return redirect('team:detail', team_id=invitation.team.id)

@login_required
def decline_invitation(request, invitation_id):
    """Decline a team invitation."""
    invitation = get_object_or_404(
        TeamInvitation,
        id=invitation_id,
        email=request.user.email,
        is_accepted=False
    )
    
    invitation.delete()
    return redirect('team:list')

@login_required
def cancel_invitation(request, team_id, invitation_id):
    """Cancel a pending team invitation."""
    team = get_object_or_404(Team, id=team_id)
    member = get_object_or_404(TeamMember, team=team, user=request.user, is_active=True)
    invitation = get_object_or_404(TeamInvitation, id=invitation_id, team=team)

    # Check permissions
    if not (member.is_admin or member.is_owner):
        return HttpResponseForbidden("You don't have permission to cancel invitations.")

    if request.method == 'POST':
        invitation.delete()
        messages.success(request, "Invitation cancelled successfully.")
    
    return redirect('team:detail', team_id=team.id)

def invited_register(request, invitation_id):
    """Special registration view for invited users."""
    # Get and validate invitation
    invitation = get_object_or_404(
        TeamInvitation,
        id=invitation_id,
        is_accepted=False,
        expires_at__gt=timezone.now()
    )
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create user but don't create default team
            user = form.save(commit=False)
            user.email = invitation.email  # Ensure email matches invitation
            user.save()
            
            # Create team membership
            TeamMember.objects.create(
                team=invitation.team,
                user=user,
                role=invitation.role,
                invited_by=invitation.invited_by
            )
            
            # Mark invitation as accepted
            invitation.is_accepted = True
            invitation.save()
            
            # Log the user in with the specific backend
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            messages.success(request, f"Welcome to {invitation.team.name}! Your account has been created and you've been added to the team.")
            return redirect('team:detail', team_id=invitation.team.id)
    else:
        form = CustomUserCreationForm(initial={'email': invitation.email})
    
    return render(request, 'team/invited_register.html', {
        'form': form,
        'invitation': invitation
    })
