from django.db import models
from broadcastcms.base.models import ContentBase, ModelBase


class Poll(ContentBase):
    class Meta:
        verbose_name = 'Poll'
        verbose_name_plural = 'Polls'


class Option(ModelBase):
    poll = models.ForeignKey(Poll, related_name='options')
    title = models.CharField(max_length=512)
    votes = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Option'
        verbose_name_plural = 'Options'

    def __unicode__(self):
        return '%s - %s' % (self.poll, self.title)
