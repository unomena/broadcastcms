from django.contrib import admin
from models import Label

class LabelAdmin(admin.ModelAdmin):
    list_display = ('title', 'visible')
    list_filter = ('visible',)
    search_fields = ('title',)

admin.site.register(Label, LabelAdmin)
