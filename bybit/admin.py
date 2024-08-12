from django.contrib import admin

from .models import Trader, Settings, Chat, EntryPrice, ErrorLog


@admin.register(ErrorLog)
class ErrorAdmin(admin.ModelAdmin):
    list_display = ('timestamp',)


admin.site.register(Trader)
admin.site.register(Settings)
admin.site.register(Chat)
admin.site.register(EntryPrice)
