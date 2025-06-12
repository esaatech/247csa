from django.contrib import admin
from .models import Ticket, TicketCategory, TicketComment, TicketAttachment

@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('teams',)

class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')

class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    readonly_fields = ('uploaded_at',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'created_by', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'category', 'teams')
    search_fields = ('title', 'description', 'created_by__email', 'assigned_to__email')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at')
    filter_horizontal = ('teams',)
    inlines = [TicketCommentInline, TicketAttachmentInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Status & Category', {
            'fields': ('status', 'priority', 'category')
        }),
        ('Assignment', {
            'fields': ('teams', 'created_by', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__email', 'ticket__title')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'ticket', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at', 'uploaded_by')
    search_fields = ('filename', 'uploaded_by__email', 'ticket__title')
    readonly_fields = ('uploaded_at',)
