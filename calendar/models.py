from django.db import models
from broadcastcms.base.models import ModelBase, ContentBase
from managers import CalendarManager


class Entry(ModelBase):
    objects = CalendarManager()

    start_date_time = models.DateTimeField(verbose_name="Starting Date & Time")
    end_date_time = models.DateTimeField(verbose_name="Ending Date & Time")
    content = models.ForeignKey(ContentBase, limit_choices_to={'is_public': True}, verbose_name='Content', related_name='entries')

    def __unicode__(self):
        return str(self.start_date_time)

    class Meta():
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
