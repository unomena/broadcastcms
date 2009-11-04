from django.contrib.auth.models import User
from django.db import models


class FacebookFriendInvite(models.Model):
    user = models.ForeignKey(User)
    fb_user_id = models.IntegerField()
    
    class Meta:
        unique_together = (
            ("user", "fb_user_id"),
        )
