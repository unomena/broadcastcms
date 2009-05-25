from django.contrib import admin
from models import Show, CastMember

class ShowAdmin(admin.ModelAdmin):
    pass

class CastMemberAdmin(admin.ModelAdmin):
    pass

admin.site.register(Show, ShowAdmin)
admin.site.register(CastMember, CastMemberAdmin)
