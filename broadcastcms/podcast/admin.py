from django.contrib import admin
from models import PodcastSeries, PodcastEpisode
from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseStackedInline

class PodcastEpisodeInline(ModelBaseStackedInline):
    model = PodcastEpisode
    fk_name = 'podcast_series'
    extra = 1


class PodcastSeriesAdmin(admin.ModelAdmin):
    inlines = (PodcastEpisodeInline,)


admin.site.register(PodcastSeries, PodcastSeriesAdmin)
