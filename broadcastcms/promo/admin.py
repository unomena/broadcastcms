from copy import deepcopy

from django.contrib import admin

from models import *
from broadcastcms.base.admin import ModelBaseAdmin

class PromoWidgetAdmin(ModelBaseAdmin):
    list_display = ('title',) + ModelBaseAdmin.list_display
    fieldsets = deepcopy(ModelBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('title',)

class PromoWidgetSlotAdmin(ModelBaseAdmin):
    list_display = ('title', 'widget',) + ModelBaseAdmin.list_display
    fieldsets = deepcopy(ModelBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('title', 'widget', 'content')

admin.site.register(PromoWidget, PromoWidgetAdmin)
admin.site.register(PromoWidgetSlot, PromoWidgetSlotAdmin)
