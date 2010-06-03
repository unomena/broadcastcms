#
# Miscellaneous video-related utility functions
#
# Thane
#

import re
from broadcastcms.video.constants import *


#------------------------------------------------------------------------------
def calculate_height(orig_width, orig_height, new_width, default=0):
    """
    Calculates the new height given the original width and height (i.e. aspect ratio) and new width.
    """
    
    height = default
    
    try:
        # get the video's aspect ratio
        aspect_ratio = float(orig_width)/float(orig_height)
        # set the video's height
        height = int(float(new_width)/aspect_ratio)
    except:
        pass
    
    return height
    


#------------------------------------------------------------------------------
def resize_embed_code(code, width, height=None):
    """
    Resizes the given embed code to the given width. If no height is specified,
    it will automatically resize it according to the given embed's aspect
    ratio.
    """
    
    # check if it's a YouTube embed
    youtube = re.compile(YOUTUBE_FULL_REGEX)
    m = youtube.match(code)
    if m:
        return YOUTUBE_EMBED_CODE % {
                'width': width, 'height': height if height else calculate_height(m.group('width1'), m.group('height1'), width),
                'videolink': m.group('videocode1'), 'domain': m.group('domain1'),
                'subdomain': m.group('subdomain1'), 'protocol': m.group('protocol1'),
            }
    else:
        # check if it's a Zoopy embed
        zoopy = re.compile(ZOOPY_FULL_REGEX)
        m = zoopy.match(code)
        if m:
            return ZOOPY_EMBED_CODE % {
                    'width': width, 'height': height if height else calculate_height(m.group('width1'), m.group('height1'), width),
                    'clsid': m.group('clsid'), 'flashversion': m.group('flashversion'), 'zoopyid': m.group('zoopyid1'),
                    'bgcolor': m.group('bgcolor1'),
                }

    # error
    return None
