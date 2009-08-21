from copy import deepcopy

from django.contrib import admin

from broadcastcms.banner.models import CodeBanner, ImageBanner
from broadcastcms.base.admin import ModelBaseAdmin

class BannerAdmin(ModelBaseAdmin):
    list_display = ('title',) + ModelBaseAdmin.list_display
    search_fields = ('title',)
    
    fieldsets = (
        (None, {'fields': ('is_public', 'title')}),
        ('Labels', {'fields': ('labels',),
                    'classes': ('collapse',),
        }),
    )

class CodeBannerAdmin(BannerAdmin):
    fieldsets = deepcopy(BannerAdmin.fieldsets)

    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('code',)

class ImageBannerAdmin(BannerAdmin):
    fieldsets = deepcopy(BannerAdmin.fieldsets)

    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('image', 'url',)


admin.site.register(CodeBanner, CodeBannerAdmin)
admin.site.register(ImageBanner, ImageBannerAdmin)
