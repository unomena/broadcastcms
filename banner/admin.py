from django.contrib import admin
from models import CodeBanner, ImageBanner

class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_public')
    list_filter = ('is_public',)
    search_fields = ('title',)
    
admin.site.register(CodeBanner, BannerAdmin)
admin.site.register(ImageBanner, BannerAdmin)
