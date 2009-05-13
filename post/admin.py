from django.contrib import admin
from broadcastcms.contentbase.admin import ContentBaseAdmin
from broadcastcms.post.models import Post

class PostAdmin(ContentBaseAdmin):
    pass

admin.site.register(Post, PostAdmin)
