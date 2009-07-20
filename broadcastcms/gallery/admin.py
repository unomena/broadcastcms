from django.contrib import admin

from broadcastcms.base.admin import ModelBaseAdmin
from broadcastcms.scaledimage.admin import ImageInline

from models import Gallery


class GalleryAdmin(ModelBaseAdmin):
    inlines = (ImageInline,)
    save_on_top = True


admin.site.register(Gallery, GalleryAdmin)
