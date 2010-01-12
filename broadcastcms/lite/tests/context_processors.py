from django.test import TestCase

from broadcastcms.lite.context_processors import section
from broadcastcms.lite.context_processors import settings
from broadcastcms.test.mocks import RequestFactory
from broadcastcms.lite.models import Settings

class ContextProcessorsTestCase(TestCase):
    def testSection(self):
        # for '/' section is 'home'
        request = RequestFactory().get('/')
        self.failUnless(section(request)['section'] == 'home')
        
        # section defaults to 'home'
        request = RequestFactory().get('/random/path')
        self.failUnless(section(request)['section'] == 'home')

        # check if section is correctly determined from path
        for path in ['home', 'shows', 'chart', 'competitions', 'news', 'events', 'galleries']:
            request = RequestFactory().get('/%s' % path)
            self.failUnless(section(request)['section'] == path)
        
        # deeper paths should not influence section
        for path in ['home', 'shows', 'chart', 'competitions', 'news', 'events', 'galleries']:
            request = RequestFactory().get('/%s/bogus/trailing/path' % path)
            self.failUnless(section(request)['section'] == path)

        # should account for paths not starting on '/'
        request = RequestFactory().get('shows')
        self.failUnless(section(request)['section'] == 'shows')

    def testSettings(self):
        request = RequestFactory().get('/')
        
        # if no settings object exists a new settings object should be created and returned
        self.failUnless(settings(request)['settings'])

        # if a settings object exists it should be returned
        site_settings = Settings.objects.get_or_create(pk='1')[0]
        self.failUnless(site_settings == settings(request)['settings'])
