from django.db import models
from broadcastcms.base.models import ContentBase
from broadcastcms.richtext.fields import RichTextField

class PodcastSeries(ContentBase):
    content = RichTextField()

    class Meta():
        verbose_name = 'Podcast Series'
        verbose_name_plural = 'Podcast Series'

class PodcastEpisode(ContentBase):
    podcast_series = models.ForeignKey(
        PodcastSeries, 
        related_name='episodes'
    )
    length = models.CharField(
        help_text="The length of the podcast in minutes.", 
        max_length=32, 
        blank=True, 
        null=True
    )
    audio = models.FileField(
        help_text="The audio clip for this podcast", 
        upload_to='content/audio'
    )
    
    class Meta():
        verbose_name = 'Podcast Episode'
        verbose_name_plural = 'Podcast Episodes'
