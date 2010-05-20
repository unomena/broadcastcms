#
# Video app for BCMS
#

from django.contrib import admin

from copy import deepcopy

from broadcastcms.base.admin import ContentBaseAdmin
from broadcastcms.base.admin import ModelBaseStackedInline
from broadcastcms.video.models import Video

class VideoAdmin(ContentBaseAdmin):
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('code',)
    save_on_top = True
    



admin.site.register(Video, VideoAdmin)
#admin.site.register(Video)