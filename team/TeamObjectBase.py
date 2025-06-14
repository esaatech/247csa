from django.db import models
from team.models import Team, TeamMember

class TeamObjectBase(models.Model):
    teams = models.ManyToManyField(Team, related_name="%(class)ss")

    class Meta:
        abstract = True

    def can_view(self, user):
        return self.teams.filter(members__user=user, members__is_active=True).exists()

    def can_edit(self, user):
        # Creator can always edit if present
        if hasattr(self, 'created_by') and self.created_by == user:
            return True
        return self.teams.filter(
            members__user=user,
            members__is_active=True,
            members__role__in=[TeamMember.Roles.ADMIN, TeamMember.Roles.OWNER]
        ).exists()

    def share_with_team(self, team):
        if not self.teams.filter(id=team.id).exists():
            self.teams.add(team)

    def unshare_with_team(self, team):
        if self.teams.count() > 1:
            self.teams.remove(team)

    def get_visible_teams(self, user):
        user_admin_teams = Team.objects.filter(
            members__user=user,
            members__is_active=True,
            members__role__in=[TeamMember.Roles.ADMIN, TeamMember.Roles.OWNER]
        )
        return user_admin_teams.exclude(id__in=self.teams.all())
