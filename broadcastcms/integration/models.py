from django.db import models
from broadcastcms.base.models import ModelBase

class FeedburnerFeed(ModelBase):
    source_url = models.CharField(
        max_length='256', 
        help_text='Source URL used by Feedburner to generate its feed.'
    )
    feedburner_url = models.CharField(
        max_length='256',
        help_text='URL pointing to Feedburner generated feed.'
    )
