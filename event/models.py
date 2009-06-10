from django.db import models
from broadcastcms.base.models import ContentBase, ModelBase
from broadcastcms.calendar.managers import CalendarManager
from broadcastcms.richtext.fields import RichTextField


class Location(ModelBase):
    name = models.CharField(max_length=255, help_text="A short descriptive name.")

    def __unicode__(self):
        return self.name


class Event(ContentBase):
    objects = CalendarManager()
    
    content = RichTextField(help_text="Full article detailing this event.")
    venue = models.CharField(max_length=255, help_text="Short venue name.")
    address = models.CharField(max_length=512, help_text="Physical venue address.")
    locations = models.ManyToManyField(Location, related_name='events', help_text="Event location(s).")
