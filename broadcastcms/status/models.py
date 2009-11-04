from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import simplejson as json

from broadcastcms.status.managers import StatusUpdateManager


class StatusUpdate(models.Model):
    SITE_SOURCE = 0
    TWITTER_SOURCE = 1
    
    SOURCE_CHOICES = (
        (SITE_SOURCE, "on site"),
        (TWITTER_SOURCE, "twitter"),
    )
    
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(default=datetime.now)
    
    text = models.CharField(max_length=160)
    source = models.IntegerField(choices=SOURCE_CHOICES)
    
    # this field stores extra data in JSON format, it can be used for storing
    # information like twitter or facebook specific details about the message
    raw_extra_data = models.TextField()
    
    objects = StatusUpdateManager()
    
    class Meta:
        ordering = ("-timestamp",)
    
    def __unicode__(self):
        return "%s set their status to %s" % (self.user, self.text)
    
    def _get_extra_data(self):
        return json.loads(self.raw_extra_data)
    
    def _set_extra_data(self, value):
        self.raw_extra_data = json.dumps(value)
    extra_data = property(_get_extra_data, _set_extra_data)
