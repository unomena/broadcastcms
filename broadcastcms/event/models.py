from django.db import models
from broadcastcms.base.models import ContentBase, ModelBase
from broadcastcms.show.models import CastMember
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
    
    def __unicode__(self):
        return self.name


class Event(ContentBase):
    objects = CalendarManager()

    content = RichTextField(help_text='Full article detailing this event.')
    castmembers = models.ManyToManyField(CastMember, blank=True, through='Appearance')

    def get_start(self):
        first_entry = self.entries.order_by('start')[0]
        return first_entry.start
    start = property(get_start)


class Location(ModelBase):
    address = models.CharField(max_length=512, help_text='Physical venue address.')
    venue = models.CharField(max_length=255, help_text='Short venue name.')
    event = models.ForeignKey(Event, related_name='locations', help_text='Event this location is for.')
    city = models.ForeignKey(
        City, related_name='locations', blank=True, null=True,
        help_text='City in which the location is present.'
    )


class Appearance(ModelBase):
    event = models.ForeignKey(Event, related_name='apearances')
    castmember = models.ForeignKey(CastMember, related_name='apearances')
