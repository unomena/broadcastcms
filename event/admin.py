from django.contrib import admin
from broadcastcms.calendar.admin import EntryInline
from models import Event, Location


class EventAdmin(admin.ModelAdmin):
    inlines = (EntryInline,)


admin.site.register(Location)
admin.site.register(Event, EventAdmin)
