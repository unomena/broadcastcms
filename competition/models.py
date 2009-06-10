from django.db import models
from broadcastcms.base.models import ContentBase
from broadcastcms.richtext.fields import RichTextField


class Competition(ContentBase):
    content = RichTextField()
    closing_date = models.DateField()
    rules = RichTextField()


class Winner(models.Model):
    competition = models.ForeignKey(Competition, related_name='winners')
    name = models.CharField(max_length=255)
    date = models.DateField()

    def __unicode__(self):
        return self.name
