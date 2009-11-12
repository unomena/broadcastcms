from datetime import datetime, timedelta

from django.test import TestCase

from models import Competition


class CompetitionTests(TestCase):
    def test_is_active(self):
        now = datetime.now().date()
        c = Competition(title='A', start=(now - timedelta(5)))
        # test the start date
        self.assertEquals(c.is_active(), True)
        c.start = now + timedelta(5)
        self.assertEquals(c.is_active(), False)
        # test the end date
        c.start = None
        c.end = now + timedelta(5)
        self.assertEquals(c.is_active(), True)
        c.end = now - timedelta(5)
        self.assertEquals(c.is_active(), False)
        # test a range
        c.start = now - timedelta(10)
        self.assertEquals(c.is_active(), False)
        c.end = now + timedelta(10)
        self.assertEquals(c.is_active(), True)
        c.start = now + timedelta(5)
        self.assertEquals(c.is_active(), False)
