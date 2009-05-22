from django.db import models
from broadcastcms.label.models import Label
from broadcastcms.base.models import ContentBase

class Show(ContentBase):
    image_scales = ((170, 96),)
    extended_description = models.TextField(verbose_name='Extended Description')
    genres = models.ManyToManyField(Label, blank=True)

    class Meta():
        verbose_name = 'Show'
        verbose_name_plural = 'Shows'
