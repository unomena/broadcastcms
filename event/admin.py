from django.contrib import admin
from broadcastcms.calendar.admin import EntryInline
from broadcastcms.base.admin import ContentBaseAdmin
from models import Event, Location, Province


class LocationInline(admin.StackedInline):
    model = Location
    fk_name = 'event'
    extra = 1

class EventAdmin(ContentBaseAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'description', 'content', 'is_public')}),
        ('Labels', {'fields': ('labels',),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('image', 'created',),
                  'classes': ('collapse',),
        }),
    )
    
    inlines = (LocationInline, EntryInline)


admin.site.register(Province)
admin.site.register(Event, EventAdmin)
