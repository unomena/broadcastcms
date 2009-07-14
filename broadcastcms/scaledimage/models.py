from django.conf import settings
from django.db import models

from storage import ScaledImageStorage


def get_image_scales(instance):
    """
    Returns a set of all the image scales attahced for this model and it's
    base classes.
    """
    app_label = instance._meta.app_label
    object_name = instance._meta.object_name
    try:
        # retrieve the scales from the project settings
        image_scales = set(settings.IMAGE_SCALES[app_label][object_name]['image'])
        # get the base classes
        if isinstance(instance, type):
            bases = instance.__bases__
        else:
            bases = instance.__class__.__bases__
        # recurse through the base classes and collect
        for base in bases:
            if issubclass(base, models.Model):
                image_scales |= get_image_scales(base)
    except AttributeError, KeyError:
        image_scales = set()
    return image_scales


def image_path_and_scales(instance, filename):
    """
    This is a very nasty little hack to specify image scales per model.
    I couldn't find a hook through which to set storage attributes prior to actual save.
    TODO: Create proper hook, see FieldFile.
    """
    # Setup image scales
    instance.image.storage.scales = get_image_scales(instance)
    # Return image path
    return 'media/content_images/%s' % filename
