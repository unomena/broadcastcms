from copy import deepcopy

from django.contrib import admin

from models import *
from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseTabularInline


class OptionInline(ModelBaseTabularInline):
    model = Option
    fk_name = 'competition'
    exclude = ['labels',]
    extra = 1


class CompetitionEntryInline(admin.TabularInline):
    model = CompetitionEntry
    fk_name = 'competition'
    extra = 1


class WinnerInline(ModelBaseTabularInline):
    model = Winner
    fk_name = 'competition'
    exclude = ['labels',]
    extra = 1


class CompetitionAdmin(ContentBaseAdmin):
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('content', 'rules', 'start', 'end')
    fieldsets += (
        ('Q&A', {'fields': ('question', 'question_blurb', 'correct_answer',),
                  'classes': ('collapse',),
        }),
    )
    
    inlines = (
        OptionInline, 
        CompetitionEntryInline,
        WinnerInline, 
    )
    save_on_top = True


admin.site.register(Competition, CompetitionAdmin)
