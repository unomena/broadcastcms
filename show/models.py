from django.db import models
from broadcastcms.label.models import Label
from broadcastcms.base.models import ModelBase, ContentBase
from broadcastcms.calendar.managers import CalendarManager

class CastMember(ModelBase):
    title = models.CharField(max_length="512")
   
    def __unicode__(self):
        return str(self.title)

    class Meta():
        verbose_name = 'Cast Member'
        verbose_name_plural = 'Cast Members'

class Show(ContentBase):
    objects = CalendarManager()

    image_scales = ((170, 96),
                    (100, 56),
                    (283, 159),
                    (158, 89),)
    extended_description = models.TextField(verbose_name='Extended Description')
    genres = models.ManyToManyField(Label, blank=True)
    rating = models.CharField(max_length="128", blank=True, default="All Ages")
    cast_members = models.ManyToManyField(CastMember, blank=True)
    homepage_url = models.URLField(max_length='512', blank=True, verbose_name="Homepage URL")

    def __unicode__(self):
        return str(self.title)
    
    class Meta():
        verbose_name = 'Show'
        verbose_name_plural = 'Shows'
