from django.core.files.storage import FileSystemStorage
from django.utils.encoding import force_unicode
from random import shuffle
from StringIO import StringIO
import cStringIO 
from PIL import Image, ImageFilter
from math import ceil
from django.core.files.uploadedfile import InMemoryUploadedFile

class ScaledImageStorage(FileSystemStorage):

    def __init__(self, scales=None, *args, **kwargs):
        self.scales = scales
        super(ScaledImageStorage, self).__init__(*args, **kwargs)

    def scale_and_crop_image(self, data, width, height):
        """
        Scales and crops an image to the requested size retaining its
        original aspect ratio. Image is sharpened after scaleing
        Use up/downsampling specific filter
        """
        image = Image.open(StringIO(data))

        orig_width, orig_height = image.size
        orig_aspect = float(orig_width) / float(orig_height)

        new_width = width
        new_height = height
        new_aspect = float(width) / float(height)
   
        if width == orig_width and height == orig_height:
            return image
    
        scaling_factor = self.scaling_factor(orig_width, orig_height, width, height)
        if scaling_factor != 1:
            #we have a scaling factor so scale
            new_width = ceil(orig_width * scaling_factor)
            new_height = ceil(orig_height * scaling_factor)
            if scaling_factor > 1:
                image = image.resize((new_width, new_height), Image.BICUBIC)
            else:
                image = image.resize((new_width, new_height), Image.ANTIALIAS)
            try:
                image = image.filter(ImageFilter.SHARPEN)
            except ValueError:
                #Some image types (i.e. pallete) can't be filtered
                pass
        if new_aspect != orig_aspect:
            #aspects are not alligned so crop
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
            #no scale change
            return 1
        if wsf < 1 and hsf < 1:
            #scale smaller
            return wsf <= hsf and hsf or wsf
        if wsf > 1 and hsf > 1:
            #scale larger
            return wsf >= hsf and wsf or hsf
        if wsf <= 1 and hsf >= 1:
            #scale width smaller but height larger:
            return hsf
        if wsf >= 1 and hsf <= 1:
            #scale width larger but height smaller:
            return wsf

    def convert_to_png(self, name, content):
        """
        We do this purely for consitency and to guarantee all image resources end in .png
        """
        content._file.seek(0)
        raw_image_data = content.read()
        image = Image.open(StringIO(raw_image_data))
        
        image_file = StringIO()
        image.save(image_file, 'PNG', quality=90)
        image_file.seek(0)
        raw_converted_image_data = image_file.read()
        content._file.seek(0)
        content._file.truncate(0)
        content._file.write(raw_converted_image_data)

        try:
            dot_index = name.rindex('.')
        except ValueError: # name has no dot
            converted_name = '%s.png' % name
        else:
            converted_name = '%s.png' % name

        return converted_name, content


    def save(self, name, content):
        """
        Saves new content to the file specified by name. The content should be a
        proper File object, ready to be read from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name
        
        content._file.seek(0)
        original_image_data = content.read()
        
        name, content = self.convert_to_png(name, content)

        name = self.get_available_name(name)
        name = self._save(name, content)

        for scale in self.scales:
            #create scale name
            width = scale[0]
            height = scale[1]
            scaled_name = name
            try:
                dot_index = scaled_name.rindex('.')
            except ValueError: # filename has no dot
                scaled_name = '%s%sx%s' % (scaled_name, width, height)
            else:
                scaled_name = '%s%sx%s%s' % (scaled_name[:dot_index], width, height, name[dot_index:])

            #create scaled content
            scaled_image = self.scale_and_crop_image(original_image_data, width, height)
            format = scaled_image.format and scaled_image.format or 'PNG'
            image_file = cStringIO.StringIO()
            scaled_image.save(image_file, format, quality=90)
            image_file.seek(0, 2)
            size = image_file.tell()
            image_file.seek(0)
            scaled_content = InMemoryUploadedFile(image_file, content.field_name, scaled_name, 'image/png', size, None)
            
            #save scaled content
            self._save(scaled_name, scaled_content)            

        # Store filenames with forward slashes, even on Windows
        return force_unicode(name.replace('\\', '/'))

    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        Filename is based on random set of 6 elements.
        """
        
        elements = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

        #Grab Path
        try:
            slash_index = name.rindex('/')
        except ValueError: #filename has no slash, hence no path
            path = ''
        else:
            path = name[:slash_index + 1]
            
        #Create initial random filename
        shuffle(elements)
        random_name = ''.join(elements[:6])
        try:
            dot_index = name.rindex('.')
        except ValueError: # filename has no dot
            name = random_name
        else:
            name = random_name + name[dot_index:]

        #Keep generating a new name until a file with that name does not exist
        while self.exists(name):
            shuffle(elements)
            random_name = ''.join(elements[:6])
            try:
                dot_index = name.rindex('.')
            except ValueError: # filename has no dot
                name = random_name
            else:
                name = random_name + name[dot_index:]
        
        #Rebuild and return full path
        return path + name
