from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Team, TeamMember, TeamInvitation
from django.utils import timezone

User = get_user_model()

@receiver(post_save, sender=User)
def create_default_team(sender, instance, created, **kwargs):
    if created:  # Only when a new user is created
        try:
            # Check if user is being created through an invitation
            has_pending_invitation = TeamInvitation.objects.filter(
                email=instance.email,
                is_accepted=False,
                expires_at__gt=timezone.now()
            ).exists()
            
            # Only create default team if user is not being invited to another team
            if not has_pending_invitation:
                # Create default team
                team_name = f"{instance.get_full_name() or instance.email}'s Team"
                team = Team.objects.create(
                    name=team_name,
                    owner=instance,
                    visibility=Team.Visibility.PRIVATE,
                    default_role=Team.DefaultRole.MEMBER
                )
                
                # Create team membership for the owner
                TeamMember.objects.create(
                    team=team,
                    user=instance,
                    role=TeamMember.Roles.OWNER,
                    invited_by=instance
                )
                
                print(f"Created default team '{team_name}' for user {instance.email}")
            else:
                print(f"Skipping default team creation for invited user {instance.email}")
            
        except Exception as e:
            print(f"Error in create_default_team signal for user {instance.email}: {str(e)}")
