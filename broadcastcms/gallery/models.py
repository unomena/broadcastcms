from django.db import models

from broadcastcms.base.models import ContentBase


class Gallery(ContentBase):
    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'


class GalleryImage(ContentBase):
    gallery = models.ForeignKey(Gallery, related_name='images')
