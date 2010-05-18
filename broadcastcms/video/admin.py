#
# Video app for BCMS
#

from django.contrib import admin

from broadcastcms.base.admin import ContentBaseAdmin
from broadcastcms.base.admin import ModelBaseStackedInline
from models import Video


class VideoAdmin(ContentBaseAdmin):
    save_on_top = True


admin.site.register(Video, VideoAdmin)
