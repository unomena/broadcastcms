from django.contrib import admin
from models import Label

class LabelAdmin(admin.ModelAdmin):
    list_display = ('title', 'visible')

admin.site.register(Label, LabelAdmin)
