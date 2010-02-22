from copy import deepcopy

from django.contrib import admin
from django.forms import models

from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseTabularInline
from broadcastcms.chart.models import AutoUpdateChart, AutoUpdateChartEntry, Chart, ChartEntry

class ChartEntryInline(ModelBaseTabularInline):
    model = ChartEntry
    fk_name = 'chart'
    exclude = ['labels', 'created']

class ChartAdmin(ContentBaseAdmin):
    inlines = (ChartEntryInline,)
    save_on_top = True

class AutoUpdateChartEntryInline(ModelBaseTabularInline):
    model = AutoUpdateChartEntry
    fk_name = 'chart'
    exclude = ['labels', 'created']

class AutoUpdateChartAdmin(ContentBaseAdmin):
    inlines = (AutoUpdateChartEntryInline,)
    
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('update_at',)
    
    save_on_top = True

admin.site.register(AutoUpdateChart, AutoUpdateChartAdmin)
admin.site.register(Chart, ChartAdmin)
