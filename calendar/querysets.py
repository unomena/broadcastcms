from datetime import datetime, timedelta
from django.db import models
from django.contrib.contenttypes.models import ContentType
from broadcastcms.base.models import ContentBase


class ContentQuerySet(models.query.QuerySet):
    def __init__(self, *args, **kwargs):
        super(ContentQuerySet, self).__init__(*args, **kwargs)
        self.content_type = ContentType.objects.get_for_model(self.model)
        self.entries = models.get_model('calendar', 'Entry').objects

    def next7days(self):
        entries = self.entries.filter(content__content_type=self.content_type).next7days()
        return self.filter(entries__in=entries).distinct()

    def next14days(self):
        entries = self.entries.filter(content__content_type=self.content_type).next14days()
        return self.filter(entries__in=entries).distinct()

    def thisweekend(self):
        entries = self.entries.filter(content__content_type=self.content_type).thisweekend()
        return self.filter(entries__in=entries).distinct()

    def thismonth(self):
        entries = self.entries.filter(content__content_type=self.content_type).thismonth()
        return self.filter(entries__in=entries).distinct()

    def nextmonth(self):
        entries = self.entries.filter(content__content_type=self.content_type).nextmonth()
        return self.filter(entries__in=entries).distinct()


class EntryQuerySet(models.query.QuerySet):
    def next7days(self):
        now = datetime.now()
        end = now + timedelta(days=7)
        return self.filter(start_date_time__range=(now, end))

    def next14days(self):
        now = datetime.now()
        end = now + timedelta(days=14)
        return self.filter(start_date_time__range=(now, end))

    def thisweekend(self):
        now = datetime.now()
        start = now + timedelta(4 - now.weekday())
        end = now + timedelta(6 - now.weekday())
        return self.filter(start_date_time__range=(start, end))

    def thismonth(self):
        now = datetime.now()
        end = datetime(now.year, (now.month+1), 1)
        return self.filter(start_date_time__range=(now, end))

    def nextmonth(self):
        now = datetime.now()
        start= datetime(now.year, (now.month+1), 1)
        end = datetime(now.year, (now.month+2), 1)
        return self.filter(start_date_time__range=(start, end))
        
