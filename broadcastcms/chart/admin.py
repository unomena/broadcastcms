from django.contrib import admin

from broadcastcms.base.admin import ModelBaseAdmin, ModelBaseTabularInline

from models import *


class SongInline(ModelBaseTabularInline):
    model = Song
    fk_name = 'chart'


class ChartAdmin(ModelBaseAdmin):
    inlines = (SongInline,)
    save_on_top = True


admin.site.register(Chart, ChartAdmin)
