from django.contrib import admin
from broadcastcms.base.admin import ContentBaseAdmin
from broadcastcms.post.models import Post

class PostAdmin(ContentBaseAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'description', 'content', 'rating', 'is_public')}),
        ('Labels', {'fields': ('labels',),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('image', 'created', 'owner'),
                  'classes': ('collapse',),
        }),
    )

admin.site.register(Post, PostAdmin)
