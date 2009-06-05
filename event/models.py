from django.db import models
from broadcastcms.base.models import ContentBase, ModelBase
from broadcastcms.calendar.managers import CalendarManager


class Location(ModelBase):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Event(ContentBase):
    objects = CalendarManager()
    venue = models.CharField(max_length=255)
    address = models.CharField(max_length=512)
    locations = models.ManyToManyField(Location, related_name='events')
