"""
This file contains various signal handlers to make sure things get translated
into HistoryEvents.
"""
from django.contrib.comments.signals import comment_was_posted
from django.contrib.contenttypes.models import ContentType

from broadcastcms.history.models import HistoryEvent


def record_comment(sender, comment, request, **kwargs):
    HistoryEvent.objects.create(user=comment.user,
        event_type=HistoryEvent.EVENT_COMMENT, content_type=comment.content_type,
        object_id=comment.object_pk)

comment_was_posted.connect(record_comment)
