from django.contrib import admin
from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'phone', 'service', 'submitted_at', 'is_read')
    list_filter   = ('service', 'is_read', 'submitted_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('name', 'email', 'phone', 'service', 'message', 'submitted_at')
    ordering      = ('-submitted_at',)
    list_per_page = 25
    date_hierarchy = 'submitted_at'

    # Mark as read when admin opens the record
    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and not obj.is_read:
            obj.is_read = True
            obj.save(update_fields=['is_read'])
        return super().change_view(request, object_id, form_url, extra_context)

    # Bulk action to mark selected submissions as read
    @admin.action(description='Mark selected submissions as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    actions = ['mark_as_read']
