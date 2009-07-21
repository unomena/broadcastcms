import random
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.utils.encoding import force_unicode
from cStringIO import StringIO
from PIL import Image, ImageFilter
from math import ceil
from django.core.files.uploadedfile import InMemoryUploadedFile
import os


class ScaledImageStorage(FileSystemStorage):

    def __init__(self, scales=[], *args, **kwargs):
        self.scales = scales
        super(ScaledImageStorage, self).__init__(*args, **kwargs)

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
        return image
    
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
        image.save(image_file, 'JPEG', quality=90)
        # create new content object
        image_file.seek(0)
        converted_content = ContentFile(image_file.read()) 

        return converted_content, converted_name

    def save(self, name, content):
        """
        Saves new content to the file specified by name. The content should be a
        proper File object, ready to be read from the beginning.
        """
        # get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name
        # convert to a singular format
        content, name = self.convert_to_jpeg(name, content)
        # get the path and the new name of the original file
        path = self.get_available_name(name)
        name = self._save('%s/original.jpeg' % path, content)
        # cycle through the scales and create the image files to match
        for scale in self.scales:
            # create scale name
            width, height = scale[0], scale[1]
            try:
                dot_index = name.rindex('.')
            except ValueError: # filename has no dot
                scaled_name = '%s/%sx%s' % (path, width, height)
            else:
                scaled_name = '%s/%sx%s%s' % (path, width, height, name[dot_index:])
            # create scaled content
            scaled_image = self.scale_and_crop_image(content, width, height)
            image_file = StringIO()
            scaled_image.save(image_file, 'JPEG', quality=85)
            image_file.seek(0)
            scaled_content = ContentFile(image_file.read())
            # save scaled content
            self._save(scaled_name, scaled_content)
            image_file.close()
        # store filenames with forward slashes, even on Windows
        return force_unicode(name.replace('\\', '/'))

    def delete(self, name):
        super(ScaledImageStorage, self).delete(name) 
        name = self.path(name)
        path = name[:name.rindex('/')]
        # delete all scaled images
        for scale in self.scales:
            width = scale[0]
            height = scale[1]
            try:
                dot_index = name.rindex('.')
            except ValueError: # filename has no dot
                scaled_name = '%s/%sx%s' % (path, width, height)
            else:
                scaled_name = '%s/%sx%s%s' % (path, width, height, name[dot_index:])
            # if the scaled file exists, delete it from the filesystem.
            if os.path.exists(scaled_name):
                os.remove(scaled_name)
        os.rmdir(path)
        
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
