from django.db import models
from django.contrib.contenttypes.models import ContentType
from querysets import ContentQuerySet, EntryQuerySet
from broadcastcms.base.models import ModelBaseManager 
from datetime import datetime, timedelta

class EntryManager(ModelBaseManager):
     
    def week(self):
        qs = self.permitted
        now = datetime.now()
        week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7) - timedelta(microseconds=1)
        return qs.filter(start_date_time__range=(week_start, week_end))

class ContentManager(ModelBaseManager):
        
    def __init__(self, *args, **kwargs):
        super(ContentManager, self).__init__(*args, **kwargs)
        self.entries = models.get_model('calendar', 'Entry').objects
    
    def week(self):
        qs = self.permitted
        content_type = ContentType.objects.get_for_model(self.model)
        entries = self.entries.week().filter(content__content_type=content_type)
        return qs.filter(entries__in=entries).distinct()
