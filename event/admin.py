from django.contrib import admin
from broadcastcms.calendar.admin import EntryInline
from broadcastcms.base.admin import ContentBaseAdmin
from models import Event, Location


class EventAdmin(ContentBaseAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'description', 'content', 'venue', 'address', 'locations', 'is_public')}),
        ('Labels', {'fields': ('labels',),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('image', 'created',),
                  'classes': ('collapse',),
        }),
    )
    
    inlines = (EntryInline,)


admin.site.register(Location)
admin.site.register(Event, EventAdmin)
