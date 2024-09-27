from django.contrib import admin
from .models import (
    TgGroup, 
    TgMessageText
)


@admin.register(TgGroup)
class TgGroupAdmin(admin.ModelAdmin):
    list_display = ("group_id", "group_name", "send_notifications", "handle_messages")
    search_fields = ("group_name", "group_id")
    list_filter = ("send_notifications", "handle_messages")

@admin.register(TgMessageText)
class TgMessageTextAdmin(admin.ModelAdmin):
    list_display = ("group", "event", "text","created_at")
    search_fields = ("group__group_name", "event", "text","created_at")
    list_filter = ("event", "group")

