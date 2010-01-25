from copy import deepcopy

from django.contrib import admin

from broadcastcms.banner.models import CodeBanner, ImageBanner
from broadcastcms.base.admin import ContentBaseAdmin

class CodeBannerAdmin(ContentBaseAdmin):
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)

    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('code',)

class ImageBannerAdmin(ContentBaseAdmin):
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)

    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('url',)


admin.site.register(CodeBanner, CodeBannerAdmin)
admin.site.register(ImageBanner, ImageBannerAdmin)
