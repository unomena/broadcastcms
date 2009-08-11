from django.contrib import admin
from models import Poll, PollOption
from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseTabularInline

class PollOptionInline(ModelBaseTabularInline):
    model = PollOption
    fk_name = 'poll'
    extra = 1


class PollAdmin(ContentBaseAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'description', 'is_public')}),
        ('Labels', {'fields': ('labels',),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('image', 'created',),
                  'classes': ('collapse',),
        }),
    )
    
    inlines = (PollOptionInline,)


admin.site.register(Poll, PollAdmin)
