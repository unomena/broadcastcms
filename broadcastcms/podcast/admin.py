from copy import deepcopy
from django.contrib import admin

from models import PodcastSeries, PodcastEpisode
from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseStackedInline

class PodcastEpisodeInline(ModelBaseStackedInline):
    model = PodcastEpisode
    fk_name = 'podcast_series'
    extra = 1


class PodcastSeriesAdmin(ContentBaseAdmin):
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('content',)
    
    inlines = (
        PodcastEpisodeInline,
    )
    save_on_top = True


admin.site.register(PodcastSeries, PodcastSeriesAdmin)
