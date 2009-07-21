from django.db import models

from broadcastcms.base.models import ContentBase
from broadcastcms.scaledimage.fields import ScaledImageField


class Gallery(ContentBase):
    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'


class Image(models.Model):
    gallery = models.ForeignKey(Gallery, related_name='images')
    image = ScaledImageField(scales=((722, 410),(80, 45)))
