from django.contrib import admin
from .models import Team, TeamMember, TeamInvitation

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__email')
    list_filter = ('created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'role', 'joined_at', 'is_active')
    list_filter = ('role', 'is_active', 'joined_at')
    search_fields = ('user__email', 'team__name')
    readonly_fields = ('id', 'joined_at')

@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'team', 'role', 'invited_by', 'created_at', 'expires_at', 'is_accepted')
    list_filter = ('role', 'is_accepted', 'created_at')
    search_fields = ('email', 'team__name', 'invited_by__email')
    readonly_fields = ('id', 'created_at')
