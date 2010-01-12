from django.contrib import admin
from django.forms import models

from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseTabularInline
from broadcastcms.chart.models import Chart, ChartEntry

class ChartAdmin(ContentBaseAdmin):
    pass

class ChartEntryAdmin(admin.ModelAdmin):
    list_display = ('song', 'chart', 'current_position', 'previous_position', 'is_public',)
    list_filter = ('chart', 'is_public',)
    search_fields = ('song__title', 'chart__title')

admin.site.register(Chart, ChartAdmin)
admin.site.register(ChartEntry, ChartEntryAdmin)
