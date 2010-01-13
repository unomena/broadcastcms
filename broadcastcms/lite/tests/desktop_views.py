from datetime import datetime, timedelta

from django.test import TestCase

from broadcastcms.show.models import Show
from broadcastcms.calendar.models import Entry

class DesktopViewsTestCase(TestCase):
    def assertSkeletonTemplatesUsed(self, response):
        self.assertTemplateUsed(response, 'desktop/base/base.html')
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/skeleton/masthead.html')
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/skeleton/account_links.html')
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/skeleton/mastfoot.html')
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/skeleton/metrics.html')
       
    def testHome(self):
        # setup

        # setup show content
        show = Show.objects.create(is_public=True)
        now = datetime.now()
        before_now = now - timedelta(minutes=10)
        after_now = now + timedelta(minutes=10)
        show_entry = Entry.objects.create(start=before_now, end=after_now, content=show, is_public=True)
        
        # generate response
        response = self.client.get('/')

        # check the response is 200 (OK)
        self.failUnlessEqual(response.status_code, 200)

        # check that the home template is used
        self.assertTemplateUsed(response, 'desktop/content/home.html')
        
        # check that skeleton templates are used
        self.assertSkeletonTemplatesUsed(response)

        # check that correct inclusion tag templates are used
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/home/features.html')
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/home/on_air.html')
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/misc/updates.html')
