import unittest

from django.conf import settings
from django.test.client import Client
from django.test import TestCase

from broadcastcms.test.mocks import RequestFactory


class ContextProcessorTestCase(unittest.TestCase):
    def setUp(self):
        from middleware import URLSwitchMiddleware
        self.url_switch = URLSwitchMiddleware()

    def testURLSwitchMiddleware(self):
        # If a request from a desktop hostname is received the desktop urls should be used.
        hostname = settings.DESKTOP_HOSTNAMES[0]
        request = RequestFactory(HTTP_HOST=hostname).get('/')
        self.url_switch.process_request(request)
        self.failUnlessEqual(settings.ROOT_URLCONF, 'broadcastcms.lite.desktop_urls')
        
        # If a request from a mobile hostname is received the mobile urls should be used.
        hostname = settings.MOBILE_HOSTNAMES[0]
        request = RequestFactory(HTTP_HOST=hostname).get('/')
        self.url_switch.process_request(request)
        self.failUnlessEqual(settings.ROOT_URLCONF, 'broadcastcms.lite.mobile_urls')
        
        # If a request from a non desktop or mobile hostname is received the desktop urls should be used.
        hostname = 'bogus hostname'
        request = RequestFactory(HTTP_HOST=hostname).get('/')
        self.url_switch.process_request(request)
        self.failUnlessEqual(settings.ROOT_URLCONF, 'broadcastcms.lite.desktop_urls')


class ViewsTestCase(TestCase):
    def testHome(self):
        response = self.client.get('/')

        #Check that response is 200 (OK)
        self.failUnlessEqual(response.status_code, 200)
