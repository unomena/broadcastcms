import unittest

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.template import RequestContext
from django.test.client import Client
from django.test import TestCase

from broadcastcms.test.mocks import RequestFactory

from templatetags.desktop_inclusion_tags import *


class MiddlewareTestCase(TestCase):
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


class DesktopViewsTestCase(TestCase):
    def testHome(self):
        response = self.client.get('/')

        #Check that response is 200 (OK)
        self.failUnlessEqual(response.status_code, 200)

class DesktopInlcusionTagsTestCase(TestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        self.context = RequestContext(request, {})
        user = User.objects.create_user('test', 'test@test.com', 'test')

    def testAccountLinks(self):
        # anonymous users should see sign in text etc
        response_string = account_links('', '').render(self.context)
        self.failUnless('Hello Stranger' in response_string)
        self.failUnless('Sign in' in response_string)
        self.failUnless('Sign up' in response_string)
        
        # authneticated users should see profile text etc
        self.context['request'].user = authenticate(username='test', password='test')
        response_string = account_links('', '').render(self.context)
        self.failUnless('Hello test' in response_string)
        self.failUnless('Profile' in response_string)
        self.failUnless('Sign out' in response_string)

    #def testMasthead(self):
    #    masthead('', '').render(self.context)
    #    self.failUnlessEqual(1, 200)
