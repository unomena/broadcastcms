from django.conf import settings
from django.test import TestCase
        
from broadcastcms.lite.middleware import URLSwitchMiddleware
from broadcastcms.test.mocks import RequestFactory

class MiddlewareTestCase(TestCase):
    def setUp(self):
        self.url_switch = URLSwitchMiddleware()

    def testURLSwitchMiddleware(self):
        # setup
        settings.URL_SWITCHES = {
            'url1:8000': 'module1.app1.urls1',
            'url2': 'module2.app2.urls2',
        }

        # ROOT_URLCONF should change for valid switches.
        for key, value in settings.URL_SWITCHES.items():
            settings.ROOT_URLCONF = 'dummy'
            request = RequestFactory(HTTP_HOST=key).get('/')
            self.url_switch.process_request(request)
            self.failUnlessEqual(settings.ROOT_URLCONF, value)
        
        # ROOT_URLCONF should not change for invalid swicthes.
        settings.ROOT_URLCONF = 'dummy'
        request = RequestFactory(HTTP_HOST='bogus_host').get('/')
        self.url_switch.process_request(request)
        self.failUnlessEqual(settings.ROOT_URLCONF, 'dummy')
