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
    question = models.CharField(
        max_length=255,
        help_text='Short competition question',
        )
    question_blurb = RichTextField(
        blank=True, 
        null=True, 
        help_text='Descriptive text elaborating on the question.'
    )
    correct_answer = models.CharField(
        max_length=255,
        blank=True, 
        null=True, 
        help_text='Answer used to determine winning entries.'
    )
    rules = RichTextField(
        blank=True, 
        null=True, 
        help_text='Rules specific to this competition.',
    )

    def is_active(self):
        now = datetime.now().date()
        active = True
        if self.start: active &= self.start <= now
        if self.end: active &= self.end >= now
        return active


class Option(ModelBase):
    competition = models.ForeignKey(Competition, related_name='options')
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title


class CompetitionEntry(models.Model):
    competition = models.ForeignKey(Competition, related_name='competition_entries')
    user = models.ForeignKey(User, related_name='competition_entries')
    answer = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Competition Entry'
        verbose_name_plural = 'Competition Entries'

    def __unicode__(self):
        return "%s answered %s" % (self.user.username, self.answer)


class Winner(ModelBase):
    competition = models.ForeignKey(Competition, related_name='winners')
    name = models.CharField(max_length=255)
    date = models.DateField()

    class Meta:
        ordering = ['-date',]

    def __unicode__(self):
        return self.name
