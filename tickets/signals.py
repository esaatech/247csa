from django.db.models.signals import post_save
from django.dispatch import receiver
from team.models import TeamMember
from .models import Ticket

@receiver(post_save, sender=Ticket)
def assign_default_team(sender, instance, created, **kwargs):
    """
    When a new ticket is created, automatically assign it to the creator's default team
    (the team where they are the owner) if no team is specified
    """
    if created and not instance.teams.exists():
        try:
            # Get the user's default team (where they are owner)
            default_team = TeamMember.objects.filter(
                user=instance.created_by,
                role=TeamMember.Roles.OWNER
            ).first()
            
            if default_team:
                instance.teams.add(default_team.team)
                print(f"Assigned ticket {instance.title} to default team: {default_team.team.name}")
            else:
                print(f"No default team found for user: {instance.created_by.email}")
                
        except Exception as e:
            print(f"Error assigning default team to ticket: {str(e)}") 