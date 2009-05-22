from django.db import models
from broadcastcms.base.models import ModelBase
from broadcastcms.scaledimage.storage import ScaledImageStorage

class Banner(ModelBase):
    title = models.CharField(max_length='512')
    
    def __unicode__(self):
        return str(self.title)
    
class CodeBanner(Banner):
    code = models.TextField()

    class Meta():
        verbose_name = "Code Banner"
        verbose_name_plural = "Code Banners"

class ImageBanner(Banner):
    image = models.ImageField(upload_to='content_images', storage=ScaledImageStorage(scales=((300, 250),)))
    url = models.URLField(max_length='512', verbose_name="URL")

    class Meta():
        verbose_name = "Image Banner"
        verbose_name_plural = "Image Banners"
