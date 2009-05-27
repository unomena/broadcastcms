from django.contrib import admin
from models import Poll, Option


class OptionInline(admin.TabularInline):
    model = Option
    fk_name = 'poll'
    extra = 1


class PollAdmin(admin.ModelAdmin):
    inlines = (OptionInline,)


admin.site.register(Poll, PollAdmin)
