from django.db import models
from broadcastcms.base.models import ModelBase
from broadcastcms.scaledimage.storage import ScaledImageStorage

class ImageBanner(ModelBase):
    title = models.CharField(max_length='512')
    image = models.ImageField(upload_to='content_images', storage=ScaledImageStorage(scales=((300, 250),)))
    url = models.URLField(max_length='512')

    def __unicode__(self):
        return str(self.title)

    class Meta():
        verbose_name = "Image Banner"
        verbose_name_plural = "Image Banners"
