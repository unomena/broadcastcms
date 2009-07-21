from django.contrib import admin

from broadcastcms.base.admin import ModelBaseAdmin

from models import Gallery, Image


class ImageInline(admin.StackedInline):
    model = Image
    extra = 1


class GalleryAdmin(ModelBaseAdmin):
    inlines = (ImageInline,)
    save_on_top = True


admin.site.register(Gallery, GalleryAdmin)
