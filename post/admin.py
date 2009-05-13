from django.contrib import admin
from broadcastcms.post.models import Post
from broadcastcms.shortcuts import comma_seperated_admin_links

def comma_seperated_admin_label_links(obj):
    return comma_seperated_admin_links(obj.labels.all())

comma_seperated_admin_label_links.short_description = 'Labels'
comma_seperated_admin_label_links.allow_tags = True

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', comma_seperated_admin_label_links)

admin.site.register(Post, PostAdmin)
