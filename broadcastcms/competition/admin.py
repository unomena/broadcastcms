from django.contrib import admin

from models import *

from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseTabularInline


class OptionInline(ModelBaseTabularInline):
    model = Option
    fk_name = 'competition'
    extra = 1


class CompetitionEntryInline(admin.TabularInline):
    model = CompetitionEntry
    fk_name = 'competition'
    extra = 1


class WinnerInline(ModelBaseTabularInline):
    model = Winner
    fk_name = 'competition'
    extra = 1


class CompetitionAdmin(ContentBaseAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'description', 'content', 'rules', 'question', 'start', 'end', 'is_public')}),
        ('Labels', {'fields': ('labels',),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('image', 'created',),
                  'classes': ('collapse',),
        }),
    )
    inlines = (OptionInline, WinnerInline, CompetitionEntryInline,)


admin.site.register(Competition, CompetitionAdmin)
