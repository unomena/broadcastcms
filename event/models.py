from django.db import models
from broadcastcms.base.models import ContentBase


class Event(ContentBase):
    image_scales = ()
    venue = models.CharField(max_length=255)
    address = models.CharField(max_length=512)
