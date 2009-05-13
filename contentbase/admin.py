from django.contrib import admin
from broadcastcms.shortcuts import comma_seperated_admin_links

def comma_seperated_admin_label_links(obj):
    return comma_seperated_admin_links(obj.labels.all())

comma_seperated_admin_label_links.short_description = 'Labels'
comma_seperated_admin_label_links.allow_tags = True

class ContentBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', comma_seperated_admin_label_links, 'public')
