from django.db import models

from broadcastcms.base.models import ContentBase, ModelBase


class Chart(ContentBase):
    class Meta:
        verbose_name = 'Chart'
        verbose_name_plural = 'Charts'


class Song(ModelBase):
    chart = models.ForeignKey(Chart, related_name='songs')
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    current_position = models.IntegerField()
    previous_position = models.IntegerField()

    class Meta:
        verbose_name = 'Song'
        verbose_name_plural = 'Songs'
