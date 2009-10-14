from cStringIO import StringIO
from math import ceil
import os 
from PIL import Image, ImageFilter
import random

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.fields.files import ImageField, ImageFieldFile
from django.utils._os import safe_join

def get_image_scales(instance):
    """
    Returns a set of all the image scales attached for this model and it's
    base classes.
    """
    # verify the object type
    if isinstance(instance, models.Model):
        bases = instance.__class__.__bases__
    elif issubclass(instance, models.Model) and not instance == models.Model:
        bases = instance.__bases__
    else: return set()

    app_label = instance._meta.app_label
    object_name = instance._meta.object_name

    
    # retrieve the scales from the project settings
    try:
        image_scales = set(settings.IMAGE_SCALES[app_label][object_name]['image'])
    except AttributeError:
        image_scales = set()
    except KeyError:
        image_scales = set()

    # recurse through the base classes and collect
    for base in bases:
        if issubclass(base, models.Model):
            image_scales |= get_image_scales(base)
    
    return image_scales

def image_path(instance, filename):
    # return image path
    return 'content/images/%s' % filename


class ScaledImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        # save original converted to jpeg
        name, content = self.convert_to_jpeg(name, content)
        path = self.get_available_name(name)
        name = '%s/original.jpeg' % path
        super(ScaledImageFieldFile, self).save(name, content, save)
      
        # save all scales
        scales = get_image_scales(self.instance)
        for scale in scales:
            # create scale name
            width, height = scale[0], scale[1]
            try:
                dot_index = name.rindex('.')
            except ValueError: # filename has no dot
                scaled_name = '%s/%sx%s' % (path, width, height)
            else:
                scaled_name = '%s/%sx%s%s' % (path, width, height, name[dot_index:])
            scaled_name = self.field.upload_to(self.field, scaled_name)

            # create scaled content
            scaled_content = self.scale_and_crop_image(content, width, height)

            # save scaled content
            self.storage.save(scaled_name, scaled_content)

        return name
    
    def get_available_name(self, name):
        """
        Generates a random 8 character path name availalbe on the storage system.
        """
        elements = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456890'
        # grab the path
        try:
            slash_index = name.rindex('/')
        except ValueError: # filename has no slash, hence no path
            path = ''
        else:
            path = name[:slash_index + 1]
        # keep generating a new name until a file with that name does not exist
        name = None
        while self.exists(name) or not name:
            name = ''.join([random.choice(elements) for n in range(8)])
        # rebuild and return full path
        return path + name
   
    def exists(self, name):
        return os.path.exists(self.path(name))

    def path(self, name):
        location = os.path.abspath(settings.MEDIA_ROOT)
        try:
            path = safe_join(location, name)
        except ValueError:
            raise SuspiciousOperation("Attempted access to '%s' denied." % name)
        return os.path.normpath(path)
    
    def scale_and_crop_image(self, content, width, height):
        """
        Scales and crops an image to the requested size retaining its
        original aspect ratio. Image is sharpened after scaleing
        Use up/downsampling specific filter
        """
        content.seek(0)
        image = Image.open(content)
        orig_width, orig_height = image.size
        orig_aspect = float(orig_width) / float(orig_height)
        # calculate new dimentions
        new_width = width
        new_height = height
        new_aspect = float(width) / float(height)
        # check if scaling is really needed
        if width == orig_width and height == orig_height:
            return image
        # calculate the scaling factor and react to it
        scaling_factor = self.scaling_factor(orig_width, orig_height, width, height)
        if scaling_factor != 1:
            # we have a scaling factor so scale
            new_width = int(ceil(orig_width * scaling_factor))
            new_height = int(ceil(orig_height * scaling_factor))
            if scaling_factor > 1:
                image = image.resize((new_width, new_height), Image.BICUBIC)
            else:
                image = image.resize((new_width, new_height), Image.ANTIALIAS)
            try:
                image = image.filter(ImageFilter.SHARPEN)
            except ValueError:
                # some image types (i.e. pallete) can't be filtered
                pass
        if new_aspect != orig_aspect:
            # aspects are not alligned so crop
            crop_left = int((new_width - width) / 2)
            crop_right = int(crop_left + width)
            crop_top = int((new_height - height) / 2)
            crop_lower = int(crop_top + height)
            crop_box = (crop_left, crop_top, crop_right, crop_lower)
            image = image.crop(crop_box)
            
        image_file = StringIO()
        image.save(image_file, 'JPEG', quality=93)
        image_file.seek(0)
        scaled_content = ContentFile(image_file.read())
        return scaled_content
    
    def scaling_factor(self, orig_width, orig_height, width, height):
        """
        """
        wsf = float(width) / float(orig_width)
        hsf = float(height) / float(orig_height)

        if wsf == 1 and hsf == 1:
            # no scale change
            return 1
        if wsf < 1 and hsf < 1:
            # scale smaller
            return wsf <= hsf and hsf or wsf
        if wsf > 1 and hsf > 1:
            # scale larger
            return wsf >= hsf and wsf or hsf
        if wsf <= 1 and hsf >= 1:
            # scale width smaller but height larger:
            return hsf
        if wsf >= 1 and hsf <= 1:
            # scale width larger but height smaller:
            return wsf

    
    def convert_to_jpeg(self, name, content):
        """
        Convert the supplied image to JPEG.
        We do this purely for consitency and to guarantee all image resources end in .jpeg
        """
        # rename the file
        try:
            dot_index = name.rindex('.')
        except ValueError: # name has no dot
            converted_name = '%s.jpeg' % name
        else:
            converted_name = '%s.jpeg' % name[:dot_index]
        # create an image from original content
        content.seek(0)
        original_image_data = content.read()
        image = Image.open(StringIO(original_image_data))
        # save as jpeg in memory
        image_file = StringIO()
        image.save(image_file, 'JPEG', quality=100)
        # create new content object
        image_file.seek(0)
        converted_content = ContentFile(image_file.read()) 

        return converted_name, converted_content

 
class ScaledImageField(ImageField):
    attr_class = ScaledImageFieldFile

    def __init__(self, *args, **kwargs):
        scales = kwargs.get('scales', [])
        if scales: del kwargs['scales']
        options = {
            'upload_to': image_path,
            'max_length':512,
        }
        options.update(kwargs)
        super(ScaledImageField, self).__init__(*args, **options)
