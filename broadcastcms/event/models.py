from django.db import models
from broadcastcms.base.models import ContentBase, ModelBase
from broadcastcms.calendar.managers import CalendarManager
from broadcastcms.richtext.fields import RichTextField


class Province(ModelBase):
    name = models.CharField(max_length=255, help_text='A short descriptive name.')

    def __unicode__(self):
        return self.name


class City(ModelBase):
    name = models.CharField(max_length=255, help_text='Name of the city')
    province = models.ForeignKey(
        Province, related_name='cities', blank=True, null=True,
        help_text='Province to which the city belongs.',
    )


class Event(ContentBase):
    objects = CalendarManager()

    content = RichTextField(help_text='Full article detailing this event.')


class Location(ModelBase):
    address = models.CharField(max_length=512, help_text='Physical venue address.')
    venue = models.CharField(max_length=255, help_text='Short venue name.')
    event = models.ForeignKey(Event, related_name='locations', help_text='Event this location is for.')
    city = models.ForeignKey(
        City, related_name='locations', blank=True, null=True,
        help_text='City in which the location is present.'
    )
