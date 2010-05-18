#
# Video app for BCMS
#

from django.db import models
from broadcastcms.base.models import ContentBase


class Video(ContentBase):
    """
    Represents a single video.
    """
    
    code = models.TextField(blank=True, null=True)
    """The HTML code to embed in the template to render the video."""
