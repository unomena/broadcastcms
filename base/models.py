from datetime import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.db.models.manager import Manager
from django.db.models.fields import FieldDoesNotExist

from broadcastcms.label.models import Label
from broadcastcms.scaledimage.storage import ScaledImageStorage

from managers import ModelBaseManager


def ensure_model_base_manager(sender, **kwargs):
    """
    Make sure all classes have the model base manager for objects 
    without overriding a child class' set manager.
    """
    cls = sender

    try:
        cls.objects
    except AttributeError:
        cls.add_to_class('objects', ModelBaseManager())
        return None
    if cls.objects.__class__ == Manager().__class__:
        cls.add_to_class('objects', ModelBaseManager())

signals.class_prepared.connect(ensure_model_base_manager)


class PermissionBase(models.Model):
    is_public = models.BooleanField(default=False, verbose_name="Public")
    
    class Meta():
        abstract = True


class ModelBase(PermissionBase):
    """
    ALL objects used on a BCMS system should inherit from ModelBase.
    ModelBase is a lightweight baseclass adding extra functionality not offered natively by Django.
    It should be seen as adding value to child classes primaraly through functions, base classes 
    should provide model fields specific to their requirements.  
    """
    default_manager = ModelBaseManager()

    content_type = models.ForeignKey(ContentType,editable=False,null=True)

    def save(self, *args, **kwargs):
        if(not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        super(ModelBase, self).save(*args, **kwargs)

    def as_leaf_class(self):
        content_type = self.content_type
        model = content_type.model_class()
        if(model == ContentBase):
            return self
        return model.objects.get(id=self.id)

        
class ContentBase(ModelBase):
    image_scales = ((78, 44), (527, 289))

    title = models.CharField(max_length='512')
    description = models.TextField()
    labels =  models.ManyToManyField(Label, blank=True)
    url = models.URLField(max_length='512', editable=False)
    created = models.DateTimeField('Created Date & Time', blank=True)
    modified = models.DateTimeField('Modified Date & Time', editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.now()
        self.modified = datetime.now()
        super(ContentBase, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def has_visible_labels(self):
        for label in self.labels.all():
            if label.is_visible:
                return True
        return False

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
