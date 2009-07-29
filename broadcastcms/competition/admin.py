from django.contrib import admin

from models import *

from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseTabularInline


class OptionInlineAdmin(ModelBaseTabularInline):
    model = Option
    fk_name = 'competition'
    extra = 1


class WinnerInlineAdmin(ModelBaseTabularInline):
    model = Winner
    fk_name = 'competition'
    extra = 1


class CompetitionAdmin(ContentBaseAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'description', 'content', 'rules', 'question', 'closing_date', 'is_public')}),
        ('Labels', {'fields': ('labels',),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('image', 'created',),
                  'classes': ('collapse',),
        }),
    )
    inlines = (OptionInlineAdmin, WinnerInlineAdmin,)


admin.site.register(Competition, CompetitionAdmin)
