from django.db import models
from broadcastcms.base.models import ModelBase, ContentBase
from managers import CalendarManager


class Entry(ModelBase):
    objects = CalendarManager()

    start = models.DateTimeField(verbose_name="Starting Date & Time", help_text="Date and time at which this calendar entry starts.")
    end = models.DateTimeField(verbose_name="Ending Date & Time", help_text="Date and time at which this calendar entry ends.")
    content = models.ForeignKey(ContentBase, limit_choices_to={'is_public': True}, verbose_name='Content', related_name='entries', help_text='Content to which this entry refers. For instance by selecting an Event you indicate that it takes place from the given starting date & time to the ending date & time.')

    def __unicode__(self):
        return '%s - %s' % (self.start, self.end)

    class Meta():
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
        ordering = ['start', 'end']
