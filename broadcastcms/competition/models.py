from django.db import models
from broadcastcms.base.models import ModelBase, ContentBase
from broadcastcms.richtext.fields import RichTextField


class Competition(ContentBase):
    content = RichTextField(help_text='Full article detailing this competition.')
    closing_date = models.DateField(blank=True, null=True, help_text='Date on which this competition closes.')
    rules = RichTextField(help_text='Rules specific to this competition.')


class Winner(ModelBase):
    competition = models.ForeignKey(Competition, related_name='winners')
    name = models.CharField(max_length=255)
    date = models.DateField()

    def __unicode__(self):
        return self.name
