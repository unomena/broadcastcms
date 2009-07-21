from django.contrib import admin
from models import *
from broadcastcms.base.admin import ModelBaseAdmin, ModelBaseTabularInline


class EntryInline(ModelBaseTabularInline):
    model = Entry
    fk_name = 'content'
    extra = 1


class EntryAdmin(ModelBaseAdmin):
    list_display = ('start', 'end', 'content', 'is_public')
    list_filter = ('is_public', 'start', 'end', 'content')
    search_fields = ('start', 'end', 'content')


admin.site.register(Entry, EntryAdmin)
