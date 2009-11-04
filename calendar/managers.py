from datetime import datetime, timedelta

from django.db import models
from django.db.models.query import Q
from django.contrib.contenttypes.models import ContentType

from broadcastcms.base.managers import ModelBaseManager, ModelBaseQuerySet
from broadcastcms.base.models import ModelBase


class CalendarQuerySet(ModelBaseQuerySet):
    def _model_specific(self, start, end):
        accessor = None
        entry_model = models.get_model('calendar', 'entry')
        entries = entry_model.objects.filter(
            Q(start_date_time__range=(start, end)) | Q(end_date_time__range=(start, end))
        )
        if self.model._meta.object_name != 'Entry':
            for relation in self.model._meta.get_all_related_objects():
                if relation.model._meta.object_name == 'Entry':
                    accessor = relation.get_accessor_name()
                    kwargs = {'%s__in' % accessor: entries}
                    # using this bad-ass query to work around stupid django
                    return self.filter(
                        pk__in=entries.filter(
                            content__id__in=self.values_list('id', flat=True)
                        ).values_list('content', flat=True)
                    )
            if accessor == None:
                raise Exception('Calendar query model has no relation to the Entry model.')
        return entries

    def next7days(self):
        start = datetime.now()
        end = start + timedelta(days=7)
        return self._model_specific(start, end)

    def next14days(self):
        start = datetime.now()
        end = start + timedelta(days=14)
        return self._model_specific(start, end)

    def thisweekend(self):
        now = datetime.now()
        start = now + timedelta(4 - now.weekday())
        end = now + timedelta(6 - now.weekday())
        return self._model_specific(start, end)

    def week(self, offset=0):
        """
        Returns entries for a week starting on Monday and ending on Sunday.
        If an offset is provided a future or past week is returned relative to the current week:
        * offset of 0 returns entries for current week (default).
        * offset of 1 returns entries for next week.
        * offset of -1 returns entries for the previous week.
        """
        now = datetime.now()
        start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        start = start + timedelta(days = offset * 7)
        end = start + timedelta(days=7) - timedelta(microseconds=1)
        return self._model_specific(start, end)

    def thismonth(self):
        start = datetime.now()
        end = datetime(start.year, (start.month+1), 1)
        return self._model_specific(start, end)

    def nextmonth(self):
        now = datetime.now()
        start = datetime(now.year, now.month, 1) + timedelta(days=32)
        start = datetime(start.year, start.month, 1)
        end = datetime(start.year, start.month, 1) + timedelta(days=32)
        end = datetime(end.year, end.month, 1)
        return self._model_specific(start, end)

    def by_content_type(self, model):
        content_type = ContentType.objects.get_for_model(model)
        return self.filter(content__content_type__exact=content_type)

class CalendarManager(ModelBaseManager):
    use_for_related_fields = True

    def get_query_set(self):
        return CalendarQuerySet(self.model)
