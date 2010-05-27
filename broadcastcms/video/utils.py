#
# Miscellaneous video-related utility functions
#
# Thane
#

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
