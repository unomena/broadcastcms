from datetime import datetime, timedelta

from django.db import models
from django.db.models.query import Q
from django.contrib.contenttypes.models import ContentType

from broadcastcms.base.managers import ModelBaseManager, ModelBaseQuerySet


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
                    return self.filter(**kwargs).distinct()
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

    def thisweek(self):
        start = datetime.now()
        end = start + timedelta(6 - start.weekday())
        return self._model_specific(start, end)

    def thismonth(self):
        start = datetime.now()
        end = datetime(start.year, (start.month+1), 1)
        return self._model_specific(start, end)

    def nextmonth(self):
        now = datetime.now()
        start = datetime(now.year, (now.month+1), 1)
        end = datetime(now.year, (now.month+2), 1)
        return self._model_specific(start, end)


class CalendarManager(ModelBaseManager):
    use_for_related_fields = True

    def get_query_set(self):
        return CalendarQuerySet(self.model)
