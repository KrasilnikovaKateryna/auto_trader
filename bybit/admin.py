from django.contrib import admin

from .models import Trader, Settings, Chat, EntryPrice, ErrorLog

admin.site.register(Trader)
admin.site.register(Settings)
admin.site.register(Chat)
admin.site.register(EntryPrice)
admin.site.register(ErrorLog)
