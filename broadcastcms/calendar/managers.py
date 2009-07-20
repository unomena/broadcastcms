from datetime import datetime, timedelta

from django.db import models
from django.db.models.query import Q
from django.contrib.contenttypes.models import ContentType

from broadcastcms.base.managers import ModelBaseManager, ModelBaseQuerySet
from broadcastcms.base.models import ContentBase


class CalendarQuerySet(ModelBaseQuerySet):
    def range(self, *args, **kwargs):
        query = self
        # capture the arguments
        if len(args) == 1: start, end = args[0], None
        elif len(args) == 2: start, end = args
        else:
            start, end = kwargs.get('start', None), kwargs.get('end', None)
        # verify the arguments
        if not (start or end):
            raise Exception('Either the start or end (or both) arguments have to be supplied.')
        # filter for the model the query is based upon
        if self.model._meta.object_name == 'Entry':
            if start:
                query = self.filter(
                    Q(start_date_time__gte=start) | Q(end_date_time__gte=start)
                )
            if end:
                query = query.filter(
                    Q(start_date_time__lte=end) | Q(end_date_time__lte=end)
                )
        else:
            if not issubclass(self.model, ContentBase):
                raise Exception('Calendar query model has to based on ContentBase.')
            entry_model = models.get_model('calendar', 'entry')
            kwargs = {
                'et':entry_model._meta.db_table,
                'ot':self.model._meta.db_table,
                'pk':self.model._meta.pk.column,
            }
            # construct where for start if supplied
            if start:
                kwargs.update({'s':start.strftime("TIMESTAMP('%Y-%m-%d %H:%M:%S')")})
                start_gte_start = '(SELECT MIN(start_date_time) FROM %(et)s WHERE %(et)s.content_id = %(ot)s.%(pk)s) >= %(s)s' % kwargs
                end_gte_start = '(SELECT MAX(end_date_time) FROM %(et)s WHERE %(et)s.content_id = %(ot)s.%(pk)s) >= %(s)s' % kwargs
            # construct where for end if supplied
            if end:
                kwargs.update({'e':end.strftime("TIMESTAMP('%Y-%m-%d %H:%M:%S')")})
                start_lte_end = '(SELECT MIN(start_date_time) FROM %(et)s WHERE %(et)s.content_id = %(ot)s.%(pk)s) <= %(e)s' % kwargs
                end_lte_end = '(SELECT MAX(end_date_time) FROM %(et)s WHERE %(et)s.content_id = %(ot)s.%(pk)s) <= %(e)s' % kwargs
            # construct the where string
            if start and end:
                where = '(%s OR %s) AND (%s OR %s)' % (start_gte_start, end_gte_start, start_lte_end, end_lte_end)
            elif start:
                where = '(%s OR %s)' % (start_gte_start, end_gte_start)
            elif end:
                where = '(%s OR %s)' % (start_lte_end, end_lte_end)
            # add to the query
            query = self.extra(where=[where,])
        return query

    def next7days(self):
        start = datetime.now()
        end = start + timedelta(days=7)
        return self.range(start, end)

    def next14days(self):
        start = datetime.now()
        end = start + timedelta(days=14)
        return self.range(start, end)

    def thisweekend(self):
        now = datetime.now()
        start = now + timedelta(4 - now.weekday())
        end = now + timedelta(6 - now.weekday())
        return self.range(start, end)

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
        return self.range(start, end)

    def thismonth(self):
        start = datetime.now()
        end = datetime(start.year, (start.month+1), 1)
        return self.range(start, end)

    def nextmonth(self):
        now = datetime.now()
        start = datetime(now.year, (now.month+1), 1)
        end = datetime(now.year, (now.month+2), 1)
        return self.range(start, end)

    def upcoming(self):
        now = datetime.now()
        return self.range(now)

    def by_content_type(self, model):
        content_type = ContentType.objects.get_for_model(model)
        return self.filter(content__content_type__exact=content_type)

    def order_by_entries(self):
        meta = self.model._meta
        for relation in meta.get_all_related_objects():
            if relation.model._meta.object_name == 'Entry':
                accessor = relation.get_accessor_name()
            if accessor :
                return self.extra(
                    select={
                        'earliest_entry':'SELECT MIN(start_date_time) FROM calendar_entry AS ca WHERE ca.content_id = %s.contentbase_ptr_id' % meta.db_table,
                    },
                    order_by=['earliest_entry',],
                )
            else:
                raise Exception('Calendar query model has no relation to the Entry model.')


class CalendarManager(ModelBaseManager):
    use_for_related_fields = True

    def get_query_set(self):
        return CalendarQuerySet(self.model)

    def range(self, *args, **kwargs):
        return self.get_query_set().range(*args, **kwargs)

    def next7days(self):
        return self.get_query_set().next7days()

    def next14days(self):
        return self.get_query_set().next14days()

    def thisweekend(self):
        return self.get_query_set().thisweekend()

    def week(self, offset=0):
        return self.get_query_set().thisweek(offset)

    def thismonth(self):
        return self.get_query_set().thismonth()

    def nextmonth(self):
        return self.get_query_set().nextmonth()

    def upcoming(self):
        return self.get_query_set().upcoming()
