from django.db import models
from broadcastcms.base.models import ContentBase

class Post(ContentBase):
    image_scales = ((100, 100), 
                    (111, 63),
                    (200, 200,))
    content = models.TextField()

    class Meta():
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
