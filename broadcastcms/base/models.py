from datetime import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.db.models.manager import Manager
from django.db.models.fields import FieldDoesNotExist
from django.template.defaultfilters import slugify

from broadcastcms.scaledimage import ScaledImageStorage, image_path_and_scales
from broadcastcms.richtext.fields import RichTextField

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
    is_public = models.BooleanField(
        default=False, verbose_name="Public",
        help_text='Check to make this item visible to the public.'
    )
    
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

    slug = models.SlugField(
        editable=False,
        max_length='275',
    )
    content_type = models.ForeignKey(
        ContentType, 
        editable=False, 
        null=True
    )
    classname = models.CharField(
        max_length=32, 
        editable=False, 
        null=True
    )

    def save(self, *args, **kwargs):
        if(not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        self.classname = self.__class__.__name__
        self.slug = self.slugify()
        super(ModelBase, self).save(*args, **kwargs)
    
    def slugify(self):
        """
        URL friendly slugs are generated using django.template.defaultfilters' slugify.
        Numbers are added to the end of slugs for uniqueness.
       
        # Slug is generated from title.
        >>> a = ContentBase(title='title')
        >>> a.slugify()
        u'title'

        # On subsequent saves slug should not change.
        >>> a.save()
        >>> a.slugify()
        u'title'
        
        # Numbers are added to slug if slug already exists.
        >>> b = ContentBase(title='title')
        >>> b.slugify()
        u'title-1'
        
        # Number tail is incremented by 1.
        >>> b.save()
        >>> c = ContentBase(title='title')
        >>> c.slugify()
        u'title-2'
        """
        slug = slugify(self.title)
        if self.slug == slug:
            return slug
        
        slugs = [content.slug for content in ContentBase.objects.all()]
        i = 1
        numbered_slug = slug
        while numbered_slug in slugs:
            numbered_slug = "%s-%s" % (slug, i)
            i += 1
        return numbered_slug

    def as_leaf_class(self):
        return self.__getattribute__(self.classname.lower())

    def delete(self, *args, **kwargs):
        for related in self._meta.get_all_related_objects():
            cascade = getattr(related.model, '_cascade', True)
            if not cascade:
                field = getattr(self, related.get_accessor_name())
                field.clear()
        super(ModelBase, self).delete(*args, **kwargs)


class ContentBase(ModelBase):
    title = models.CharField(
        max_length='256', help_text='A short descriptive title.'
    )
    description = models.TextField(
        help_text='A short description. More verbose than the title but limited to one or two sentences.'
    )
    labels =  models.ManyToManyField(
        'label.Label', blank=True, help_text='Labels categorizing this item.'
    )
    created = models.DateTimeField(
        'Created Date & Time', blank=True,
        help_text='Date and time on which this item was created. This is automatically set on creation, but can be changed subsequently.'
    )
    modified = models.DateTimeField(
        'Modified Date & Time', editable=False,
        help_text='Date and time on which this item was last modified. This is automatically set each time the item is saved.'
    )
    image = models.ImageField(
        upload_to=image_path_and_scales, storage=ScaledImageStorage(),
        help_text='Image associated with this item. The uploaded image will be automatically scaled and cropped to required resolutions.'
    )
    rating = models.IntegerField(
        blank=True,
        null=True,
        choices=[(n, str(n)) for n in range(1,6)],
        help_text='Rating for this item.',
    )

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
