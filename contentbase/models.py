from django.db import models
from broadcastcms.permissionbase.models import PermissionBase
from broadcastcms.label.models import Label
from broadcastcms.scaledimage.storage import ScaledImageStorage

class ContentBase(PermissionBase):
    title = models.CharField(max_length='512')
    description = models.TextField()
    labels = models.ManyToManyField(Label, blank=True)
    image = models.ImageField(upload_to='content_images', storage=ScaledImageStorage())
