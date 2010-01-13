from copy import deepcopy

from django.contrib import admin

from models import *
from broadcastcms.base.admin import ModelBaseAdmin, ModelBaseTabularInline

class PromoWidgetSlotInline(ModelBaseTabularInline):
    model = PromoWidgetSlot
    fk_name = 'widget'
    exclude = ['labels',]
    extra = 2

class PromoWidgetAdmin(ModelBaseAdmin):
    list_display = ('title',) + ModelBaseAdmin.list_display
    fieldsets = deepcopy(ModelBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('title',)
    inlines = (
        PromoWidgetSlotInline, 
    )
    save_on_top = True

admin.site.register(PromoWidget, PromoWidgetAdmin)
