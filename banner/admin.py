from django.contrib import admin
from models import ImageBanner

class ImageBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_public')
    list_filter = ('is_public',)
    search_fields = ('title',)

admin.site.register(ImageBanner, ImageBannerAdmin)
