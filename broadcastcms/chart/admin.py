from django.contrib import admin

from broadcastcms.base.admin import ModelBaseAdmin, ModelBaseTabularInline

from models import *


class ChartEntryInline(ModelBaseTabularInline):
    model = ChartEntry
    fk_name = 'chart'


class ChartAdmin(ModelBaseAdmin):
    inlines = (ChartEntryInline,)
    save_on_top = True


admin.site.register(Chart, ChartAdmin)
