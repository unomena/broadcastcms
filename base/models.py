from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.db.models.manager import Manager
from django.db.models.fields import FieldDoesNotExist

from broadcastcms.label.models import Label
from broadcastcms.scaledimage.storage import ScaledImageStorage
from broadcastcms.richtext.fields import RichTextField

from managers import ModelBaseManager

def get_image_scales(instance):
    app_label = instance._meta.app_label
    object_name = instance._meta.object_name
    try:
        image_scales = settings.IMAGE_SCALES[app_label][object_name]['image']
    except KeyError:
        image_scales = ()
    return image_scales


def get_base_image_scales(instance):
    """
    Collect all base class image scales
    """
    image_scales = ()
    for base in instance.__class__.__bases__:
        image_scales += get_image_scales(base)
    
    return image_scales

    
def image_path_and_scales(instance, filename):
    """
    This is a very nasty little hack to specify image scales per model.
    I couldn't find a hook through which to set storage attributes prior to actual save.
    TODO: Create proper hook, see FieldFile.
    """
    # Setup image scales
    instance.image.storage.scales = get_image_scales(instance) + get_base_image_scales(instance)
    # Return image path
    return 'media/content_images/%s' % filename


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
    is_public = models.BooleanField(default=False, verbose_name="Public", help_text='Check to make this item visible to the public.')
    
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
    classname = models.CharField(max_length=32, editable=False, null=True)

    def save(self, *args, **kwargs):
        if(not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        
        self.classname = self.__class__.__name__
        super(ModelBase, self).save(*args, **kwargs)

    def as_leaf_class(self):
        return self.__getattribute__(self.classname.lower())


class ContentBase(ModelBase):
    title = models.CharField(max_length='512')
    description = RichTextField()
    labels =  models.ManyToManyField(Label, blank=True)
    url = models.URLField(max_length='512', editable=False)
    created = models.DateTimeField('Created Date & Time', blank=True)
    modified = models.DateTimeField('Modified Date & Time', editable=False)
    image = models.ImageField(upload_to=image_path_and_scales, storage=ScaledImageStorage())

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
