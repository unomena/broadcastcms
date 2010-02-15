from datetime import datetime
import re

from django.contrib.auth.models import User
from django.db import models
from django.utils import simplejson as json
from django.utils.html import urlize
from django.utils.safestring import mark_safe
        
from broadcastcms.status.managers import StatusUpdateManager

class StatusUpdate(models.Model):
    SITE_SOURCE = 0
    TWITTER_SOURCE = 1
    
    SOURCE_CHOICES = (
        (SITE_SOURCE, "on site"),
        (TWITTER_SOURCE, "twitter"),
    )
    
    key = models.CharField(max_length=40, blank=True, editable=False)
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

    def urlize_text(self):
        """
        Urlizes links, including twitter links(see http://www.djangosnippets.org/snippets/1445/)
        """
        urlized_text = urlize(self.text, nofollow=True)
        if self.source == self.TWITTER_SOURCE:
            urlized_text = re.sub(r'(\s+|\A)@([a-zA-Z0-9\-_]*)\b',r'\1<a href="http://twitter.com/\2">@\2</a>', urlized_text)
            # Link hash tags
            urlized_text = re.sub(r'(\s+|\A)#([a-zA-Z0-9\-_]*)\b',r'\1<a href="http://search.twitter.com/search?q=%23\2">#\2</a>', urlized_text)

        # add target blank to achor tags
        split_text = urlized_text.split("href=")
        urlized_text = 'target="_blank" href='.join(split_text)

        return mark_safe(urlized_text)
