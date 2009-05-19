from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals

from broadcastcms.permissionbase.models import PermissionBase
from broadcastcms.label.models import Label
from broadcastcms.scaledimage.storage import ScaledImageStorage

class ContentBase(PermissionBase):
    title = models.CharField(max_length='512')
    description = models.TextField()
    labels = models.ManyToManyField(Label, blank=True)
    url = models.URLField(max_length='512', editable=False)
    image_scales = ((78, 44), (527, 289))
    content_type = models.ForeignKey(ContentType,editable=False,null=True)

    def save(self):
        if(not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        self.save_base()

    def as_leaf_class(self):
        content_type = self.content_type
        model = content_type.model_class()
        if(model == ContentBase):
            return self
        return model.objects.get(id=self.id)
        
def get_base_scales(obj):
    """
    Collect all base class image scales
    """
    image_scales = ()
    for base in obj.__bases__:
        if hasattr(base, 'image_scales'):
            image_scales += base.image_scales
    return image_scales

def add_scales(sender, **kwargs):
    """
    Create core image field on class_prepared so that child 
    classes can specify their own ScaledImageStorage scales.

    TODO: There is some fun here with long inheritance chains where parent and child classes both save images
    Make sure only child classes actually save images.
    """
    if hasattr(sender, 'image_scales'):
        sender.image_scales = sender.image_scales + get_base_scales(sender)
        sender.add_to_class('image', models.ImageField(upload_to='content_images', storage=ScaledImageStorage(scales=sender.image_scales)))

signals.class_prepared.connect(add_scales)
