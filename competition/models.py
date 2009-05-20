from django.db import models
from broadcastcms.base.models import ContentBase


class Competition(ContentBase):
    pass


class CompetitionWinner(models.Model):
    competition = models.ForeignKey(Competition, related_name='winners')
    name = models.CharField(max_length=255)
    date = models.DateField()

    def __unicode__(self):
        return self.name
