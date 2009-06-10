from django.contrib import admin
from models import *


class EntryInline(admin.TabularInline):
    model = Entry
    fk_name = 'content'
    extra = 1


class EntryAdmin(admin.ModelAdmin):
    list_display = ('start_date_time', 'end_date_time', 'content', 'is_public')
    list_filter = ('is_public', 'start_date_time', 'end_date_time', 'content')
    search_fields = ('start_date_time', 'end_date_time', 'content')


admin.site.register(Entry, EntryAdmin)
