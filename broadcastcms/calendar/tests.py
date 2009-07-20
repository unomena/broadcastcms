from datetime import datetime, timedelta

from django.test import TestCase
from django.db import models
from django.core.management import call_command

from broadcastcms.base.models import ContentBase

from managers import CalendarManager
from models import Entry


class CalendarManagerTests(TestCase):
    def setUp(self):
        # define a class that uses calendar entries
        class ContentModel(ContentBase):
            objects = CalendarManager()
        models.register_models('calendar', ContentModel)
        self.model = ContentModel
        call_command('syncdb', verbosity=0, interactive=False)

    def generateStandardEntries(self):
        now = datetime.now()
        objA = self.model.objects.create()
        objB = self.model.objects.create()
        objC = self.model.objects.create()
        objD = self.model.objects.create()
        Entry.objects.create(
            start_date_time=(now - timedelta(days=35)),
            end_date_time=(now - timedelta(days=15)),
            content=objA,
        )
        Entry.objects.create(
            start_date_time=(now - timedelta(days=12)),
            end_date_time=(now - timedelta(days=8)),
            content=objA,
        )
        Entry.objects.create(
            start_date_time=(now - timedelta(days=1)),
            end_date_time=(now + timedelta(days=1)),
            content=objB,
        )
        Entry.objects.create(
            start_date_time=(now + timedelta(days=8)),
            end_date_time=(now + timedelta(days=12)),
            content=objC,
        )
        Entry.objects.create(
            start_date_time=(now + timedelta(days=15)),
            end_date_time=(now + timedelta(days=35)),
            content=objC,
        )
        Entry.objects.create(
            start_date_time=(now + timedelta(days=40)),
            end_date_time=(now + timedelta(days=60)),
            content=objD,
        )

    def testRange(self):
        now = datetime.now()
        entries = Entry.objects
        objects = self.model.objects
        self.generateStandardEntries()
        # setup time markers
        thirtydays = now + timedelta(30)
        tendays = now + timedelta(10)
        zerodays = now
        minustendays = now - timedelta(10)
        minusthirtydays = now - timedelta(30)
        # check basic counts
        self.assertEquals(entries.count(), 6)
        self.assertEquals(objects.count(), 4)
        # test entries with just start
        self.assertEquals(entries.range(thirtydays).count(), 2)
        self.assertEquals(entries.range(tendays).count(), 3)
        self.assertEquals(entries.range(zerodays).count(), 4)
        self.assertEquals(entries.range(minustendays).count(), 5)
        # test objects with just start
        self.assertEquals(objects.range(thirtydays).count(), 2)
        self.assertEquals(objects.range(tendays).count(), 2)
        self.assertEquals(objects.range(zerodays).count(), 3)
        self.assertEquals(objects.range(minustendays).count(), 4)
        # test entries with just end
        self.assertEquals(entries.range(end=minusthirtydays).count(), 1)
        self.assertEquals(entries.range(end=minustendays).count(), 2)
        self.assertEquals(entries.range(end=zerodays).count(), 3)
        self.assertEquals(entries.range(end=tendays).count(), 4)
        # test objects with just end
        self.assertEquals(objects.range(end=minusthirtydays).count(), 1)
        self.assertEquals(objects.range(end=minustendays).count(), 1)
        self.assertEquals(objects.range(end=zerodays).count(), 2)
        self.assertEquals(objects.range(end=tendays).count(), 3)
        # test entries with both start and end
        self.assertEquals(entries.range(minusthirtydays, minustendays).count(), 2)
        self.assertEquals(entries.range(minusthirtydays, zerodays).count(), 3)
        self.assertEquals(entries.range(minustendays, zerodays).count(), 2)
        self.assertEquals(entries.range(zerodays, tendays).count(), 2)
        self.assertEquals(entries.range(zerodays, thirtydays).count(), 3)
        self.assertEquals(entries.range(tendays, thirtydays).count(), 2)
        self.assertEquals(entries.range(minusthirtydays, thirtydays).count(), 5)
        # test objects with both start and end
        self.assertEquals(objects.range(minusthirtydays, minustendays).count(), 1)
        self.assertEquals(objects.range(minusthirtydays, zerodays).count(), 2)
        self.assertEquals(objects.range(minustendays, zerodays).count(), 2)
        self.assertEquals(objects.range(zerodays, tendays).count(), 2)
        self.assertEquals(objects.range(zerodays, thirtydays).count(), 2)
        self.assertEquals(objects.range(tendays, thirtydays).count(), 1)
        self.assertEquals(objects.range(minusthirtydays, thirtydays).count(), 3)
        # test ranges inside entry ranges for entries
        self.assertEquals(entries.range(minusthirtydays, minusthirtydays).count(), 1)
        self.assertEquals(entries.range(thirtydays, thirtydays).count(), 1)
        # test ranges inside entry ranges for objects
        self.assertEquals(objects.range(minusthirtydays, minusthirtydays).count(), 1)
        self.assertEquals(objects.range(thirtydays, thirtydays).count(), 1)

    def testNext7Days(self):
        self.generateStandardEntries()
        self.assertEquals(Entry.objects.all().next7days().count(), 1)
        self.assertEquals(self.model.objects.all().next7days().count(), 1)

    def testNext14Days(self):
        self.generateStandardEntries()
        self.assertEquals(Entry.objects.all().next14days().count(), 2)
        self.assertEquals(self.model.objects.all().next14days().count(), 2)

    def testThisWeekend(self):
        pass

    def testWeek(self):
        pass

    def testThisMonth(self):
        pass

    def testNextMonth(self):
        pass

    def testUpcoming(self):
        pass
