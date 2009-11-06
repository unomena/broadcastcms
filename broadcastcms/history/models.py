from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class HistoryEvent(models.Model):
    EVENT_LIKED = 0
    EVENT_COMMENT = 1
    EVENT_STATUS = 2
    EVENT_FRIEND = 3
    EVENT_VOTE = 4
    
    EVENT_TYPES = (
        (EVENT_LIKED, "liked"),
        (EVENT_COMMENT, "commented"),
        (EVENT_STATUS, "status"),
        (EVENT_FRIEND, "friended"),
        (EVENT_VOTE, "voted"),
    )
    
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(default=datetime.now)
    event_type = models.IntegerField(choices=EVENT_TYPES)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    content_object = GenericForeignKey()
    
    def __unicode__(self):
        return "%s had an event of type %s with %s" % (
            self.user,
            self.get_event_type_display(),
            self.content_object
        )
