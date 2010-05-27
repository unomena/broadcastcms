#
# Video app for BCMS
#

from django.db import models
from broadcastcms.base.models import ContentBase
#~ from django.contrib import admin


class Video(ContentBase):
    """
    Represents a single video.
    """
    
    VIDEO_TYPES = (
        ('y', 'YouTube'),
        ('z', 'Zoopy'),
    )
    
    video_type = models.CharField(max_length=1, choices=VIDEO_TYPES)
    """What kind of video is this?"""
    
    video_id = models.CharField(max_length=30, blank=True)
    """A unique ID for this video, whose structure depends on what kind of video it is."""
    
    code = models.TextField(blank=True, null=True)
    """The HTML code to embed in the template to render the video."""


#~ admin.site.register(Video)
