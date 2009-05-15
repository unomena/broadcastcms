from django.core.files.storage import FileSystemStorage
from random import randint

class ScaledImageStorage(FileSystemStorage):

    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        # Filename is based on random set of elements.
        # If the filename already exists, keep adding a random element to the name
        # of the file until the filename doesn't exist.
        
        elements = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

        #Grab Path
        try:
            slash_index = name.rindex('/')
        except ValueError: #filename has no slash, hence no path
            path = ''
        else:
            path = name[:slash_index + 1]
            
        #Reset name to initial single random element plus extension
        try:
            dot_index = name.rindex('.')
        except ValueError: # filename has no dot
            name = elements[randint(0, len(elements) - 1)]
        else:
            name = elements[randint(0, len(elements) - 1)] + name[dot_index:]

        #Keep adding elements to the filename until a file with that name does not exist
        while self.exists(name):
            try:
                dot_index = name.rindex('.')
            except ValueError: # filename has no dot
                name += elements[randint(0, len(elements) - 1)]
            else:
                name = name[:dot_index] + elements[randint(0, len(elements) - 1)] + name[dot_index:]
        
        #Rebuild and return full path
        return path + name
