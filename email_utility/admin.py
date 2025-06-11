from django.contrib import admin
from django.utils.html import format_html
from django_mailbox.models import Message
from django.utils.safestring import mark_safe
from .models import MailboxConfiguration


@admin.register(MailboxConfiguration)
class MailboxConfigurationAdmin(admin.ModelAdmin):
    list_display = ('email_display', 'provider_type', 'last_sync', 'sync_enabled', 'folder_count', 'sync_status')
    list_filter = ('sync_enabled', 'email_config__provider_type')
    search_fields = ('email_config__email', 'email_config__user__username')
    readonly_fields = ('last_sync', 'folder_list', 'mailbox_uri')
    fieldsets = (
        ('Configuration', {
            'fields': ('email_config', 'mailbox', 'sync_enabled')
        }),
        ('Sync Information', {
            'fields': ('last_sync', 'mailbox_uri')
        }),
        ('Folder Configuration', {
            'fields': ('custom_folders', 'folder_list'),
            'classes': ('collapse',)
        }),
    )

    def email_display(self, obj):
        return f"{obj.email_config.email}"
    email_display.short_description = 'Email'
    
    def provider_type(self, obj):
        return obj.email_config.get_provider_type_display()
    provider_type.short_description = 'Provider'
    
    def folder_count(self, obj):
        return len(obj.folders)
    folder_count.short_description = 'Folders'
    
    def sync_status(self, obj):
        if obj.sync_enabled:
            if obj.last_sync:
                return format_html(
                    '<span style="color: green;">✓ Last sync: {}</span>',
                    obj.last_sync.strftime('%Y-%m-%d %H:%M')
                )
            return format_html('<span style="color: orange;">⚠ Never synced</span>')
        return format_html('<span style="color: red;">✗ Disabled</span>')
    sync_status.short_description = 'Status'
    
    def folder_list(self, obj):
        folders = obj.folders
        html = '<ul>'
        for name, path in folders.items():
            html += f'<li><strong>{name}</strong>: {path}</li>'
        html += '</ul>'
        return format_html(html)
    folder_list.short_description = 'Available Folders'
    
    def mailbox_uri(self, obj):
        """Show mailbox URI with password hidden"""
        uri = obj.mailbox.uri if obj.mailbox else ''
        if uri:
            # Hide password in URI
            parts = uri.split('@')
            if len(parts) > 1:
                user_pass = parts[0].split(':')
                if len(user_pass) > 1:
                    uri = f"{user_pass[0]}:****@{parts[1]}"
        return uri
    mailbox_uri.short_description = 'Mailbox URI'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(email_config__user=request.user)
        return qs
    
    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        if request.user.is_superuser:
            return True
        return obj.email_config.user == request.user

# Get the model admin class without registering
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = (
        'subject_display',
        'from_display',
        'to_display',
        'received_time',
        'has_attachments'
    )
    list_filter = (
        'processed',
        'read',
        'outgoing',
        ('mailbox', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        'subject',
        'from_header',
        'to_header',
        'body'
    )
    readonly_fields = (
        'message_id',
        'mailbox',
        'from_header',
        'to_header',
        'subject',
        'processed',
        'read',
        'body_html',
        'encoded_attachments',
    )
    
    fieldsets = (
        ('Message Details', {
            'fields': (
                'subject',
                'from_header',
                'to_header',
                'processed',
                'read',
            )
        }),
        ('Message Content', {
            'fields': ('body_html',),
        }),
        ('Attachments', {
            'fields': ('encoded_attachments',),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': (
                'message_id',
                'mailbox',
                'outgoing',
            ),
            'classes': ('collapse',)
        }),
    )

    def subject_display(self, obj):
        icon = '📤' if obj.outgoing else '📥'
        read_status = '👁️' if obj.read else '🔵'
        return format_html(
            '{} {} {}',
            icon,
            read_status,
            obj.subject or '(No Subject)'
        )
    subject_display.short_description = 'Subject'
    
    def from_display(self, obj):
        return obj.from_header
    from_display.short_description = 'From'
    
    def to_display(self, obj):
        return obj.to_header
    to_display.short_description = 'To'
    
    def received_time(self, obj):
        return obj.processed.strftime('%Y-%m-%d %H:%M')
    received_time.short_description = 'Received'
    
    def has_attachments(self, obj):
        return bool(obj.attachments.count())
    has_attachments.boolean = True
    has_attachments.short_description = '📎'

    def body_html(self, obj):
        """Display email body with basic styling"""
        return mark_safe(f'''
            <div style="
                max-height: 400px;
                overflow-y: auto;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            ">
                {obj.body}
            </div>
        ''')
    body_html.short_description = 'Message Body'

    def encoded_attachments(self, obj):
        """Display attachments list"""
        attachments = obj.attachments.all()
        if not attachments:
            return '(No attachments)'
            
        html = '<ul>'
        for attachment in attachments:
            html += f'''
                <li>
                    📎 {attachment.get_filename()} 
                    ({format_size(attachment.file.size)})
                </li>
            '''
        html += '</ul>'
        return mark_safe(html)
    encoded_attachments.short_description = 'Attachments'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(mailbox__user_config__email_config__user=request.user)
        return qs

def format_size(size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

# Try to unregister if registered
try:
    admin.site.unregister(Message)
except admin.sites.NotRegistered:
    pass

# Now register our custom admin
admin.site.register(Message, EmailMessageAdmin)

