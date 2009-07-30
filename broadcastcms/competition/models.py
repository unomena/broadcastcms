from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from broadcastcms.base.models import ModelBase, ContentBase
from broadcastcms.base.managers import ModelBaseManager
from broadcastcms.richtext.fields import RichTextField


class Competition(ContentBase):
    content = RichTextField(help_text='Full article detailing this competition.')
    start = models.DateField(blank=True, null=True, help_text='Date on which this competition opens.')
    end = models.DateField(blank=True, null=True, help_text='Date on which this competition ends.')
    rules = RichTextField(help_text='Rules specific to this competition.')
    question = RichTextField(blank=True, null=True, help_text='Question to be answered by contestants.')

    def is_active(self):
        now = datetime.now().date()
        active = True
        if self.start: active &= self.start < now
        if self.end: active &= self.end > now
        return active


class Option(ModelBase):
    competition = models.ForeignKey(Competition, related_name='options')
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title


class CompetitionEntry(models.Model):
    competition = models.ForeignKey(Competition, related_name='competition_entries')
    user = models.ForeignKey(User, related_name='competition_entries')
    option = models.ForeignKey(Option, related_name='competition_entries')
    timestamp = models.DateTimeField(auto_now_add=True)


class Winner(ModelBase):
    competition = models.ForeignKey(Competition, related_name='winners')
    name = models.CharField(max_length=255)
    date = models.DateField()

    class Meta:
        ordering = ['-date',]

    def __unicode__(self):
        return self.name
