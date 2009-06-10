from django.contrib import admin
from models import Poll, Option
from broadcastcms.base.admin import ContentBaseAdmin

class OptionInline(admin.TabularInline):
    model = Option
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
    
    inlines = (OptionInline,)


admin.site.register(Poll, PollAdmin)
