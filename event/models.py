from django.db import models
from broadcastcms.base.models import ContentBase, ModelBase
from broadcastcms.calendar.managers import CalendarManager
from broadcastcms.richtext.fields import RichTextField


class Province(ModelBase):
    name = models.CharField(max_length=255, help_text='A short descriptive name.')

    def __unicode__(self):
        return self.name


class Event(ContentBase):
    objects = CalendarManager()

    content = RichTextField(help_text='Full article detailing this event.')


class Location(ModelBase):
    address = models.CharField(max_length=512, help_text='Physical venue address.')
    venue = models.CharField(max_length=255, help_text='Short venue name.')
    event = models.ForeignKey(Event, related_name='locations', help_text='Event this location is for.')
    province = models.ForeignKey(Province, related_name='locations', help_text='Province of the location.')
