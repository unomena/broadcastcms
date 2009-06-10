from django.db import models
from broadcastcms.label.models import Label
from broadcastcms.base.models import ModelBase, ContentBase
from broadcastcms.calendar.managers import CalendarManager
from broadcastcms.richtext.fields import RichTextField

class CastMember(ModelBase):
    title = models.CharField(max_length="256", help_text="Full cast member name.")
   
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
    extended_description = RichTextField(verbose_name='Extended Description', help_text="Full article detailing this show.")
    genres = models.ManyToManyField(Label, related_name="genres", blank=True, limit_choices_to={'restricted_to__contains': 'show-genres'})
    rating = models.CharField(max_length="128", blank=True, default="All Ages", help_text="Age restriction rating.")
    cast_members = models.ManyToManyField(CastMember, blank=True, help_text="Show cast members.")
    homepage_url = models.URLField(max_length='512', blank=True, verbose_name="Homepage URL", help_text="External URL to show's homepage.")

    def __unicode__(self):
        return str(self.title)
    
    class Meta():
        verbose_name = 'Show'
        verbose_name_plural = 'Shows'
