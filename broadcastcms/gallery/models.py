from django.db import models

from broadcastcms.base.models import ContentBase
from broadcastcms.scaledimage.models import Image


class Gallery(ContentBase):
    images = models.ManyToManyField(Image, related_name='galleries')

    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'
