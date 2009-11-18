from django.contrib.auth.models import User
from django.db import models

from broadcastcms.facebook_integration.managers import (
    FacebookFriendInviteManager
)

class FacebookFriendInvite(models.Model):
    user = models.ForeignKey(User)
    fb_user_id = models.IntegerField()
    
    objects = FacebookFriendInviteManager()
    
    class Meta:
        unique_together = (
            ("user", "fb_user_id"),
        )
