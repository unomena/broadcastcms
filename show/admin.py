from django.contrib import admin
from broadcastcms.calendar.admin import EntryInline
from models import Show, CastMember


class ShowAdmin(admin.ModelAdmin):
    inlines = (EntryInline,)


admin.site.register(Show, ShowAdmin)
admin.site.register(CastMember)
