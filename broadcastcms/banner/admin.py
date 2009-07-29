from django.contrib import admin

from models import CodeBanner, ImageBanner
from broadcastcms.base.admin import ModelBaseAdmin

class BannerAdmin(ModelBaseAdmin):
    list_display = ('title', 'is_public')
    list_filter = ('is_public',)
    search_fields = ('title',)

admin.site.register(CodeBanner, BannerAdmin)
admin.site.register(ImageBanner, BannerAdmin)
