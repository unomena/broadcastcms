from django.contrib import admin

from broadcastcms.base.admin import ContentBaseAdmin
from models import Gallery, Image


class ImageInline(admin.StackedInline):
    model = Image


class GalleryAdmin(ContentBaseAdmin):
    inlines = (
        ImageInline,
    )
    save_on_top = True


admin.site.register(Gallery, GalleryAdmin)
