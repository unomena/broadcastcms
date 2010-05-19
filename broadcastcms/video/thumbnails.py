#
# Functions to get thumbnails for videos.
#
# thane
#

import urllib
import cStringIO
try:
    import json
except:
    import simplejson as json

from django.core.files.uploadedfile import InMemoryUploadedFile


#------------------------------------------------------------------------------
def jpeg_to_inmemoryfile(response, filename):
    """
    Writes the given response (assuming it's a JPEG) to an InMemoryUploadedFile
    object.
    """
    
    size = len(response)
    f = cStringIO.StringIO()
    f.write(response)
    return InMemoryUploadedFile(f, 'image', filename, 'image/jpeg', size, None)



#------------------------------------------------------------------------------
def get_youtube_thumbnail(id):
    """
    Retrieves a thumbnail for the YouTube video with the specified ID, returns
    an InMemoryUploadedFile on success or None on error.
    """
    
    try:
        response = urllib.urlopen('http://i4.ytimg.com/vi/%s/0.jpg' % id).read()
    except:
        return None
        
    # convert it to an InMemoryUploadedFile
    return jpeg_to_inmemoryfile(response, 'youtube_thumbnail')



#------------------------------------------------------------------------------
def get_zoopy_thumbnail(id):
    """
    Retrieves a thumbnail for the Zoopy video with the specified ID, returns
    an InMemoryUploadedFile on success or None on error.
    """
    
    try:
        response = urllib.urlopen('http://api.zoopy.com/zoopy/0.1/rest/media/search.json?include=%s' % id).read()
        # decode the json object
        obj = json.loads(response)
        thumb_url = obj['result']['media'][0]['thumbnail']
        # get the thumbnail URL
        response = urllib.urlopen(thumb_url).read()
    except:
        # failure at any point - return nothing
        return None
        
    # convert it to an InMemoryUploadedFile
    return jpeg_to_inmemoryfile(response, 'zoopy_thumbnail')
