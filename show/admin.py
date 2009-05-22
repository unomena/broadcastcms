from django.contrib import admin
from models import Show

class ShowAdmin(admin.ModelAdmin):
    pass

admin.site.register(Show, ShowAdmin)
