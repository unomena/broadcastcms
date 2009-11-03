from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

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
    
    objects = StatusUpdateManager()
    
    class Meta:
        ordering = ("-timestamp",)
    
    def __unicode__(self):
        return "%s set their status to %s" % (self.user, self.text)
