from django.db import models
from querysets import ContentQuerySet, EntryQuerySet


class EntryManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return EntryQuerySet(self.model)


class CalendarManager(models.Manager):
    def get_query_set(self):
        return ContentQuerySet(self.model)
