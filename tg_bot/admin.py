from django.contrib import admin
from .models import TgGroup
from .models import TgMessageText


class TgGroupAdmin(admin.ModelAdmin):
    list_display = ("group_id", "group_name", "send_notifications", "handle_messages")
    search_fields = ("group_name", "group_id")
    list_filter = ("send_notifications", "handle_messages")


class TgMessageTextAdmin(admin.ModelAdmin):
    list_display = ("group", "event", "text")
    search_fields = ("group__group_name", "event", "text")
    list_filter = ("event", "group")


admin.site.register(TgMessageText, TgMessageTextAdmin)

admin.site.register(TgGroup, TgGroupAdmin)
