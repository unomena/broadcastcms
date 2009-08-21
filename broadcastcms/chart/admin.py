from django.contrib import admin
from django.forms import models

from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseTabularInline
from broadcastcms.chart.models import Chart, ChartEntry

class ChartEntryInline(ModelBaseTabularInline):
    model = ChartEntry
    fk_name = 'chart'
    exclude = ['labels',]


class ChartAdmin(ContentBaseAdmin):
    inlines = (ChartEntryInline,)
    save_on_top = True


admin.site.register(Chart, ChartAdmin)
