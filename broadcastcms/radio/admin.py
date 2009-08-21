from copy import deepcopy

from django.contrib import admin

from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseTabularInline
from models import Artist, Song, Credit

class CreditInline(ModelBaseTabularInline):
    model = Credit

class ArtistAdmin(ContentBaseAdmin):
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('content',)
    
    inlines = (
        CreditInline,
    )
    save_on_top = True

class SongAdmin(ContentBaseAdmin):
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('album', 'video_embed',)
    
    inlines = (
        CreditInline,
    )
    save_on_top = True


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Song, SongAdmin)
