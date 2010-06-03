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
        return code
    else:
        # check if it's a Zoopy embed
        zoopy = re.compile(ZOOPY_FULL_REGEX)
        m = zoopy.match(code)
        if m:
            return code

    # error
    return None
