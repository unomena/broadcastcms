from copy import deepcopy

from django.contrib import admin

from broadcastcms.base.admin import ModelBaseAdmin
from broadcastcms.pagebuilder.models import Page, OutgoingPage

class OutgoingPageInline(admin.TabularInline):
    model = OutgoingPage
    fk_name = 'page'

class PageAdmin(ModelBaseAdmin):
    list_display = ('title',) + ModelBaseAdmin.list_display
    
    fieldsets = deepcopy(ModelBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('title', 'query', 'menu', 'view',)
    inlines = (
        OutgoingPageInline, 
    )
    save_on_top = True

admin.site.register(Page, PageAdmin)
