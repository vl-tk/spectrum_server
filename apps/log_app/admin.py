from django.contrib import admin

from .models import LogRecord


@admin.register(LogRecord)
class LogRecordAdmin(admin.ModelAdmin):

    list_display = [
        'pk',
        'user',
        'message',
        'content_type',
        'object_id',
        'is_admin_only',
        'created_at',
        'updated_at'
    ]

    list_filter = [
        'is_admin_only'
    ]

    search_fields = [
        'user',
        'message'
    ]
