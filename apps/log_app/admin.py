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
        'created_at',
        'updated_at'
    ]
