from django.db import models
from broadcastcms.base.models import ContentBase
from broadcastcms.richtext.fields import RichTextField

class Post(ContentBase):
    content = RichTextField()

    class Meta():
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
