from django.contrib import admin
from models import Competition, Winner
from broadcastcms.base.admin import ContentBaseAdmin


class WinnerInlineAdmin(admin.TabularInline):
    model = Winner
    extra = 1


class CompetitionAdmin(ContentBaseAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'description', 'content', 'rules', 'closing_date', 'is_public')}),
        ('Labels', {'fields': ('labels',),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('image', 'created',),
                  'classes': ('collapse',),
        }),
    )
    inlines = (WinnerInlineAdmin,)


admin.site.register(Competition, CompetitionAdmin)
