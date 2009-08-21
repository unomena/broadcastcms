from copy import deepcopy

from django.contrib import admin

from broadcastcms.calendar.admin import EntryInline
from broadcastcms.base.admin import ModelBaseAdmin, ContentBaseAdmin, ModelBaseStackedInline, ModelBaseTabularInline
from models import Event, City, Location, Province


class LocationInline(ModelBaseTabularInline):
    model = Location
    fk_name = 'event'
    exclude = ['labels',]


class EventAdmin(ContentBaseAdmin):
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('content',)

    inlines = (
        LocationInline, 
        EntryInline
    )
    save_on_top = True


class CityInline(ModelBaseTabularInline):
    model = City
    fk_name = 'province'
    exclude = ['labels',]


class CityAdmin(ModelBaseAdmin):
    list_display = ('name', 'province',) + ModelBaseAdmin.list_display
    list_filter = ('province',) + ModelBaseAdmin.list_filter
    search_fields = ('name',)

    fieldsets = deepcopy(ModelBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('name', 'province')


class ProvinceAdmin(ModelBaseAdmin):
    list_display = ('name',) + ModelBaseAdmin.list_display

    fieldsets = deepcopy(ModelBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('name',)
    
    inlines = (CityInline,)
    save_on_top = True


admin.site.register(City, CityAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(Event, EventAdmin)
