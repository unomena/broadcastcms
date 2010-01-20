from datetime import datetime, timedelta

from django.test import TestCase

from broadcastcms.show.models import Show
from broadcastcms.calendar.models import Entry
from broadcastcms.base.models import ContentBase
from broadcastcms.promo.models import PromoWidget, PromoWidgetSlot
from broadcastcms.lite.models import Settings

class DesktopViewsTestCase(TestCase):
    def testHome(self):
        # check the response is 200 (OK)
        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 200)
