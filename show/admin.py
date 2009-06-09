from django.contrib import admin
from broadcastcms.calendar.admin import EntryInline
from broadcastcms.base.admin import ContentBaseAdmin, comma_seperated_admin_label_links
from broadcastcms.shortcuts import comma_seperated_admin_links
from models import Show, CastMember

def comma_seperated_admin_genre_links(obj):
    return comma_seperated_admin_links(obj.genres.all())

comma_seperated_admin_genre_links.short_description = 'Genres'
comma_seperated_admin_genre_links.allow_tags = True

class ShowAdmin(ContentBaseAdmin):
    list_display = ('title', 'description', comma_seperated_admin_label_links, comma_seperated_admin_genre_links, 'created', 'modified', 'is_public')
    list_filter = ('labels', 'genres', 'is_public', 'created', 'modified')
    
    inlines = (EntryInline,)
    fieldsets = (
        (None, {'fields': ('title', 'description', 'extended_description', 'rating', 'homepage_url', 'is_public')}),
        ('Labels', {'fields': ('labels', 'genres'),
                    'classes': ('collapse',),
        }),
        ('Cast & Crew', {'fields': ('cast_members',),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('image', 'created',),
                  'classes': ('collapse',),
        }),
    )


admin.site.register(Show, ShowAdmin)
admin.site.register(CastMember)
