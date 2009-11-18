from django.db import models

from friends.models import Friendship


class FacebookFriendInviteManager(models.Manager):
    def create_friendships(self, user, facebook_id):
        """
        Creates friendships for users who invited a Facebook friend.
        """
        for invite in self.filter(fb_user_id=facebook_id):
            Friendship.objects.create(from_user=invite.user, to_user=user)
            invite.delete()
