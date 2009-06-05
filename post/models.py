from django.db import models
from broadcastcms.base.models import ContentBase

class Post(ContentBase):
    content = models.TextField()

    class Meta():
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
