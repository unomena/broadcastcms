from copy import deepcopy
from django.contrib import admin
from models import Poll, PollOption
from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseTabularInline

class PollOptionInline(ModelBaseTabularInline):
    model = PollOption
    fk_name = 'poll'
    exclude = ['labels',]


class PollAdmin(ContentBaseAdmin):
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('content',)
    inlines = (
        PollOptionInline,
    )
    save_on_top = True


admin.site.register(Poll, PollAdmin)
