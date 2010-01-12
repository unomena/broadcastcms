from django.conf import settings
from django.test import TestCase
        
from broadcastcms.lite.middleware import URLSwitchMiddleware
from broadcastcms.test.mocks import RequestFactory

class MiddlewareTestCase(TestCase):
    def setUp(self):
        self.url_switch = URLSwitchMiddleware()
        settings.ROOT_URLCONF = 'dummy'
        settings.URL_SWITCHES = {
            'url1': 'module1.app1.urls1',
            'url2': 'module2.app2.urls2',
        }

    def testURLSwitchMiddleware(self):
        # request urlconf should not be changed or set for invalid hosts.
        request = RequestFactory(HTTP_HOST='bogus_host').get('/')
        self.url_switch.process_request(request)
        self.failIf(hasattr(request, 'urlconf'))

        # request urlconf should change for valid switches.
        for key, value in settings.URL_SWITCHES.items():
            request = RequestFactory(HTTP_HOST=key).get('/')
            self.url_switch.process_request(request)
            self.failUnlessEqual(request.urlconf, value)
