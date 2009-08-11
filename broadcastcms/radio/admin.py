from django.contrib import admin

from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseTabularInline

from models import *

class CreditInline(ModelBaseTabularInline):
    model = Credit
    extra = 1

class ArtistAdmin(admin.ModelAdmin):
    inlines = (CreditInline,)

class SongAdmin(admin.ModelAdmin):
    inlines = (CreditInline,)


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(Credit)
