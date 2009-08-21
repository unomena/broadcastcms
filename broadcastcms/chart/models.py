from django.db import models

from broadcastcms.base.models import ContentBase, ModelBase
from broadcastcms.base.managers import ModelBaseManager
from broadcastcms.radio.models import Song


class Chart(ContentBase):
    class Meta:
        verbose_name = 'Chart'
        verbose_name_plural = 'Charts'


class ChartEntry(ModelBase):
    chart = models.ForeignKey(Chart, related_name='chartentries')
    song = models.ForeignKey(Song, related_name='chartentries')
    current_position = models.IntegerField()
    previous_position = models.IntegerField()

    class Meta:
        verbose_name = 'Song'
        verbose_name_plural = 'Songs'
        ordering = ['current_position',]

    def __unicode__(self):
        return '%s entry %s' % (self.chart.title, self.current_position)
