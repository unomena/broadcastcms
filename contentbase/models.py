from django.db import models
from broadcastcms.permissionbase.models import PermissionBase
from broadcastcms.label.models import Label
from broadcastcms.scaledimage.storage import ScaledImageStorage
from django.db.models import signals

class ContentBase(PermissionBase):
    title = models.CharField(max_length='512')
    description = models.TextField()
    labels = models.ManyToManyField(Label, blank=True)
    image_scales = ((500, 500), 
                    (400, 400),)

def add_scales(sender, **kwargs):
    """
    Create core image field on class_prepared so that child 
    classes can specify their own ScaledImageStorage scales.

    #TODO: On inheritance both parent and child classes gets an image field.
    Add a check to prevent this.
    """
    sender.add_to_class('image', models.ImageField(upload_to='content_images', storage=ScaledImageStorage(scales=sender.image_scales)))

signals.class_prepared.connect(add_scales)
