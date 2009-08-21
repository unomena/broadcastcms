from copy import deepcopy

from django.contrib import admin

from broadcastcms.calendar.admin import EntryInline
from broadcastcms.base.admin import ModelBaseAdmin, ContentBaseAdmin, comma_seperated_admin_label_links
from broadcastcms.shortcuts import comma_seperated_admin_links
from models import Show, CastMember


def comma_seperated_admin_genre_links(obj):
    return comma_seperated_admin_links(obj.genres.all())

comma_seperated_admin_genre_links.short_description = 'Genres'
comma_seperated_admin_genre_links.allow_tags = True


class ShowAdmin(ContentBaseAdmin):
    list_display = ContentBaseAdmin.list_display + (comma_seperated_admin_genre_links,)
    list_filter = ContentBaseAdmin.list_filter + ('genres',)
    search_fields = ContentBaseAdmin.search_fields + ('extended_description',)
   
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('extended_description', 'classification', 'homepage_url')
        elif fieldset[0] == 'Labels':
            fieldset[1]['fields'] += ('genres',)

    fieldsets += (
        ('Cast & Crew', {'fields': ('castmembers',), 
                         'classes': ('collapse',),}),
    )
    
    inlines = (
        EntryInline,
    )
    save_on_top = True


class CastMemberAdmin(ContentBaseAdmin):
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('content', )


admin.site.register(Show, ShowAdmin)
admin.site.register(CastMember, CastMemberAdmin)
