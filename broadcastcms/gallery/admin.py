from django.contrib import admin

from broadcastcms.base.admin import ContentBaseAdmin
from broadcastcms.base.admin import ModelBaseStackedInline
from models import Gallery, GalleryImage

class GallerImageInline(ModelBaseStackedInline):
    model = GalleryImage
    fk_name = 'gallery'
    exclude = ['created', 'rating', 'owner', 'labels',]
    extra = 1


class GalleryAdmin(ContentBaseAdmin):
    inlines = (
        GallerImageInline,
    )
    save_on_top = True


admin.site.register(Gallery, GalleryAdmin)
