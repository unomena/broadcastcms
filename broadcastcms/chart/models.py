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

class AutoUpdateChart(Chart):
    update_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time at which to automatically update this chart. Updating iterates over chart entries and sets previous positions to current positions and current positions to next positions, whilst clearing next positions."
    )
    
    class Meta:
        verbose_name = 'Auto Update Chart'
        verbose_name_plural = 'Auto Update Charts'

    def update_entries(self):
        """
        Updates chart entries. 
        Previous positions become current positions. 
        Current positions becomes next positions.
        Next positions are set to None.
        update_at field is set to None.
        """
        if self.update_at:
            if (datetime.now() >= self.update_at):
                for entry in self.chartentries.all():
                    entry = entry.as_leaf_class()
                    entry.previous_position = entry.current_position
                    if entry.next_position != None:
                        entry.current_position = entry.next_position
                        entry.next_position = None
                    entry.save()
                    self.update_at = None
                    self.save()

class AutoUpdateChartEntry(ChartEntry):
    next_position = models.IntegerField(
        blank=True,
        null=True,
    )
