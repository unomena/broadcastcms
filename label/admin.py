from django.contrib import admin
from models import Label

class LabelAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_visible')
    list_filter = ('is_visible',)
    search_fields = ('title',)

admin.site.register(Label, LabelAdmin)
