from django.contrib import admin
from broadcastcms.calendar.admin import EntryInline
from models import Event


class EventAdmin(admin.ModelAdmin):
    inlines = (EntryInline,)


admin.site.register(Event, EventAdmin)
