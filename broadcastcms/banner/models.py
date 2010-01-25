from django.db import models
from broadcastcms.base.models import ContentBase

class Banner(ContentBase):
    pass
    
class CodeBanner(Banner):
    code = models.TextField(help_text='The full HTML/Javascript code snippet to be embedded for this banner.')

    class Meta():
        verbose_name = "Code Banner"
        verbose_name_plural = "Code Banners"

class ImageBanner(Banner):
    url = models.CharField(
        max_length='512', 
        verbose_name="URL", 
        help_text='URL (internal or external) to which this banner will link.'
    )

    class Meta():
        verbose_name = "Image Banner"
        verbose_name_plural = "Image Banners"
