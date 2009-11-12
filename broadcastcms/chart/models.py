from datetime import datetime

from django.db import models

from broadcastcms.base.models import ContentBase, ModelBase
from broadcastcms.base.managers import ModelBaseManager
from broadcastcms.radio.models import Song


class Chart(ContentBase):
    class Meta:
        verbose_name = 'Chart'
        verbose_name_plural = 'Charts'


class ChartEntry(ModelBase):
    chart = models.ForeignKey(
        Chart, 
        related_name='chartentries'
    )
    song = models.ForeignKey(
        Song, 
        related_name='chartentries'
    )
    current_position = models.IntegerField()
    previous_position = models.IntegerField()
    created = models.DateTimeField(
        'Created Date & Time', 
        blank=True,
        help_text='Date and time on which this item was created. This is automatically set on creation, but can be changed subsequently.'
    )

    class Meta:
        verbose_name = 'Chart Entry'
        verbose_name_plural = 'Chart Entries'
        ordering = ['current_position',]

    def __unicode__(self):
        return '%s entry %s' % (self.chart.title, self.current_position)
    
    def save(self, *args, **kwargs):
        if not self.id and not self.created:
            self.created = datetime.now()
        super(ChartEntry, self).save(*args, **kwargs)
