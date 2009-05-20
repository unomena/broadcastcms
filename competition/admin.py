from django.contrib import admin
from models import Competition, Winner


class WinnerInlineAdmin(admin.TabularInline):
    model = Winner
    extra = 1


class CompetitionAdmin(admin.ModelAdmin):
    inlines = (WinnerInlineAdmin,)


admin.site.register(Competition, CompetitionAdmin)
