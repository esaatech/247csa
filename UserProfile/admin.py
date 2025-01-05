from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'email_domain', 'phone_number', 'role', 'display_avatar', 'created_at')
    list_filter = ('email_domain', 'role', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'phone_number')
    readonly_fields = ('email_domain', 'created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'company_name', 'phone_number', 'role', 'avatar')
        }),
        ('OAuth Details', {
            'fields': ('oauth_token', 'refresh_token', 'token_expires_at'),
            'classes': ('collapse',),
            'description': 'OAuth authentication details'
        }),
        ('System Fields', {
            'fields': ('email_domain', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Automatically managed fields'
        })
    )

    def display_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.avatar.url)
        return "No avatar"
    display_avatar.short_description = 'Avatar'

    def save_model(self, request, obj, form, change):
        if not obj.email_domain and obj.user.email:
            obj.email_domain = obj.user.email.split('@')[-1]
        super().save_model(request, obj, form, change)
