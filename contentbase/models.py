from django.db import models

from broadcastcms.permissionbase.models import PermissionBase
from broadcastcms.label.models import Label

class ContentBase(PermissionBase):
    title = models.CharField(max_length='512')
    description = models.TextField()
    labels = models.ManyToManyField(Label, blank=True)
