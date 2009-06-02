from django.contrib import admin
from broadcastcms.calendar.admin import EntryInline
from broadcastcms.base.admin import ContentBaseAdmin
from models import Show, CastMember


class ShowAdmin(ContentBaseAdmin):
    inlines = (EntryInline,)
    fieldsets = (
        (None, {'fields': ('title', 'description', 'extended_description', 'rating', 'homepage_url', 'is_public')}),
        ('Labels', {'fields': ('labels', 'genres'),
                    'classes': ('collapse',),
        }),
        ('Cast & Crew', {'fields': ('cast_members',),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('image', 'created',),
                  'classes': ('collapse',),
        }),
    )


admin.site.register(Show, ShowAdmin)
admin.site.register(CastMember)
