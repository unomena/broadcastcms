from django.contrib import admin
from models import Show, CastMember, Timeslot

class ShowAdmin(admin.ModelAdmin):
    pass

class CastMemberAdmin(admin.ModelAdmin):
    pass

class TimeslotAdmin(admin.ModelAdmin):
    list_display = ('start_date_time', 'end_date_time', 'show', 'is_public')
    list_filter = ('show', 'is_public',)
    search_fields = ('start_date_time', 'end_date_time', 'show')

admin.site.register(Show, ShowAdmin)
admin.site.register(CastMember, CastMemberAdmin)
admin.site.register(Timeslot, TimeslotAdmin)
