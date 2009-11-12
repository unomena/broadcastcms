from django.db import models
from broadcastcms.base.models import ModelBase
from broadcastcms.scaledimage import ScaledImageField

class Banner(ModelBase):
    title = models.CharField(
        max_length='256', 
        help_text='A short descriptive title.'
    ) 
    description = models.TextField(
        help_text='A short description. More verbose than the title but limited to one or two sentences.'
    )
    
    def __unicode__(self):
        return self.title
    
class CodeBanner(Banner):
    code = models.TextField(help_text='The full HTML/Javascript code snippet to be embedded for this banner.')

    class Meta():
        verbose_name = "Code Banner"
        verbose_name_plural = "Code Banners"

class ImageBanner(Banner):
    image = ScaledImageField(
        help_text='Image to be used for this banner.', 
    )
    url = models.CharField(
        max_length='512', 
        verbose_name="URL", 
        help_text='URL (internal or external) to which this banner will link.'
    )

    class Meta():
        verbose_name = "Image Banner"
        verbose_name_plural = "Image Banners"
