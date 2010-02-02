"""
This file contains various signal handlers to make sure things get translated
into ActivityEvents.
"""
from django.contrib.comments.signals import comment_was_posted
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

from friends.models import Friendship
from voting.models import Vote

from broadcastcms.activity.models import ActivityEvent
from broadcastcms.status.models import StatusUpdate


def record_comment(sender, comment, request, **kwargs):
    if request.user.is_authenticated():
        ActivityEvent.objects.create(user=comment.user,
            event_type=ActivityEvent.EVENT_COMMENT,
            content_type=ContentType.objects.get_for_model(comment),
            object_id=comment.pk)
        
comment_was_posted.connect(record_comment)

def record_friendship(sender, instance, raw, created, **kwargs):
    if created:
        ct = ContentType.objects.get_for_model(instance.from_user)
        ActivityEvent.objects.create(user=instance.to_user,
            event_type=ActivityEvent.EVENT_FRIEND,
            content_type=ct, object_id=instance.from_user.pk)
        ActivityEvent.objects.create(user=instance.from_user,
            event_type=ActivityEvent.EVENT_FRIEND,
            content_type=ct, object_id=instance.to_user.pk)

#post_save.connect(record_friendship, sender=Friendship)

def record_vote(sender, instance, raw, created, **kwargs):
    if created:
        ActivityEvent.objects.create(user=instance.user,
            event_type=ActivityEvent.EVENT_VOTE,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk)

post_save.connect(record_vote, sender=Vote)

def record_status_update(sender, instance, raw, created, **kwargs):
    if created:
        ActivityEvent.objects.create(user=instance.user,
            event_type=ActivityEvent.EVENT_STATUS,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk)

post_save.connect(record_status_update, sender=StatusUpdate)
