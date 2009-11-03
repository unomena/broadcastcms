from django.db import models
from broadcastcms.base.models import ModelBase
from broadcastcms.scaledimage.storage import ScaledImageStorage

class Banner(ModelBase):
    title = models.CharField(max_length='256', help_text='A short descriptive title.')
    
    def __unicode__(self):
        return self.title
    
class CodeBanner(Banner):
    code = models.TextField(help_text='The full HTML/Javascript code snippet to be embedded for this banner.')

    class Meta():
        verbose_name = "Code Banner"
        verbose_name_plural = "Code Banners"

class ImageBanner(Banner):
    image = models.ImageField(upload_to='content_images', help_text='Image to be used for this banner.', storage=ScaledImageStorage(scales=((300, 250),)))
    url = models.URLField(max_length='512', verbose_name="URL", help_text='URL (internal or external) to which this banner will link.')

    class Meta():
        verbose_name = "Image Banner"
        verbose_name_plural = "Image Banners"
