"""
This file contains various signal handlers to make sure things get translated
into HistoryEvents.
"""
from django.contrib.comments.signals import comment_was_posted
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

from friends.models import Friendship

from broadcastcms.history.models import HistoryEvent


def record_comment(sender, comment, request, **kwargs):
    HistoryEvent.objects.create(user=comment.user,
        event_type=HistoryEvent.EVENT_COMMENT, content_type=comment.content_type,
        object_id=comment.object_pk)

comment_was_posted.connect(record_comment)

def record_friendship(sender, instance, raw, created, **kwargs):
    if created:
        HistoryEvent.objects.create(user=instance.to_user,
            event_type=HistoryEvent.EVENT_FRIEND,
            content_type=ContentType.get_for_model(instance.from_user),
            object_id=instance.from_user.pk)
        HistoryEvent.objects.create(user=instance.from_user,
            event_type=HistoryEvent.EVENT_FRIEND,
            content_type=ContentType.get_for_model(instance.to_user),
            object_id=instance.to_user.pk)

post_save.connect(record_friendship, sender=Friendship)
