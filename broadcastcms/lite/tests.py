import unittest
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.template import RequestContext
from django.test.client import Client
from django.test import TestCase

from broadcastcms.test.mocks import RequestFactory
from broadcastcms.base.models import ContentBase

from models import Settings
from templatetags.desktop_inclusion_tags import *

class ContextProcessorsTestCase(TestCase):
    def testSection(self):
        from context_processors import section

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
        from context_processors import settings

        request = RequestFactory().get('/')
        
        # if no settings object exists a new settings object should be created and returned
        self.failUnless(settings(request)['settings'])

        # if a settings object exists it should be returned
        site_settings = Settings.objects.get_or_create(pk='1')[0]
        self.failUnless(settings(request)['settings'] == site_settings)
            
class MiddlewareTestCase(TestCase):
    def setUp(self):
        from middleware import URLSwitchMiddleware
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

class DesktopViewsTestCase(TestCase):
    def assertSkeletonTemplatesUsed(self, response):
        self.assertTemplateUsed(response, 'desktop/sections/base.html')
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/skeleton/masthead.html')
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/skeleton/account_links.html')
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/skeleton/mastfoot.html')
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/skeleton/metrics.html')
        
    def testHome(self):
        response = self.client.get('/')

        # check the response is 200 (OK)
        self.failUnlessEqual(response.status_code, 200)

        # check that the home template was used
        self.assertTemplateUsed(response, 'desktop/content/home.html')
        
        # check that skeleton templates were used
        self.assertSkeletonTemplatesUsed(response)


class DesktopInlcusionTagsTestCase(TestCase):
    def setContext(self, path):
        request = RequestFactory().get(path)
        self.context = RequestContext(request, {})

    def testAccountLinks(self):
        # setup
        self.setContext(path='/')
        user = User.objects.create_user('test', 'test@test.com', 'test')
        
        # anonymous users receive sign in text etc
        response_string = account_links('', '').render(self.context)
        self.failUnless('Hello Stranger' in response_string)
        self.failUnless('Sign in' in response_string)
        self.failUnless('Sign up' in response_string)
        
        # authenticated users receive profile text etc
        self.context['request'].user = authenticate(username='test', password='test')
        response_string = account_links('', '').render(self.context)
        self.failUnless('Hello test' in response_string)
        self.failUnless('Profile' in response_string)
        self.failUnless('Sign out' in response_string)

    def testMasthead(self):
        # setup
        self.setContext(path='/')
        
        # no item should be highlighted when on home
        response_string = masthead('', '').render(self.context)
        self.failIf('class="on"' in response_string)
        
        # appropriate menu section should be highlighted for each path
        for path in ['/shows/line-up/', '/chart/', '/competitions/', '/news/', '/events/', '/galleries/']:
            self.setContext(path=path)
            response_string = masthead('', '').render(self.context)
            correct_highlight = '<li class="on"><a href="%s">' % path
            self.failUnless(correct_highlight in response_string)

        # test search bar
        site_settings = Settings.objects.get_or_create(pk='1')[0]

        # don't display search if settings doesn't have a gcs partner id.
        site_settings.gcs_partner_id = ''
        site_settings.save()
        self.setContext(path='/')
        response_string = masthead('', '').render(self.context)
        self.failIf('search' in response_string)
        
        # display search with correct partner id if settings has a gcs partner id.
        site_settings.gcs_partner_id = 'partner-pub-id'
        site_settings.save()
        self.setContext(path='/')
        response_string = masthead('', '').render(self.context)
        self.failUnless('search' in response_string and 'partner-pub-id' in response_string)

    def testMastfoot(self):
        # setup
        self.setContext(path='/')
        site_settings = Settings.objects.get_or_create(pk='1')[0]

        # does the current year display as the copyright year 
        response_string = mastfoot('', '').render(self.context)
        self.failUnless(str(datetime.now().year) in response_string)
        
        # the mobile link should only render if settings.MOBILE_HOSTNAME is specified 
        settings.MOBILE_HOSTNAME = None
        response_string = mastfoot('', '').render(self.context)
        self.failIf('View mobile version' in response_string)
        settings.MOBILE_HOSTNAME = 'localhost'
        response_string = mastfoot('', '').render(self.context)
        self.failUnless('View mobile version' in response_string)
        
        # check if t&c link renders properly.
        # don't render the link if no content has been supplied.
        response_string = mastfoot('', '').render(self.context)
        self.failIf('Terms and Conditions' in response_string)
        # render the link when content has been supplied.
        site_settings.terms = "Arbitrary text"
        site_settings.save()
        self.setContext(path='/')
        response_string = mastfoot('', '').render(self.context)
        self.failUnless('Terms and Conditions' in response_string)
        
        # check if privacy policy link renders properly.
        # don't render the link if no content has been supplied.
        response_string = mastfoot('', '').render(self.context)
        self.failIf('Privacy Policy' in response_string)
        # render the link when content has been supplied.
        site_settings.privacy = "Arbitrary text"
        site_settings.save()
        self.setContext(path='/')
        response_string = mastfoot('', '').render(self.context)
        self.failUnless('Privacy Policy' in response_string)
        
        # check if about link renders properly.
        # don't render the link if no content has been supplied.
        response_string = mastfoot('', '').render(self.context)
        self.failIf('About Us' in response_string)
        # render the link when content has been supplied.
        site_settings.about = "Arbitrary text"
        site_settings.save()
        self.setContext(path='/')
        response_string = mastfoot('', '').render(self.context)
        self.failUnless('About Us' in response_string)
        
        # check if advertise link renders properly.
        # don't render the link if no content has been supplied.
        response_string = mastfoot('', '').render(self.context)
        self.failIf('Advertise' in response_string)
        # render the link when content has been supplied.
        site_settings.advertise = "Arbitrary text"
        site_settings.save()
        self.setContext(path='/')
        response_string = mastfoot('', '').render(self.context)
        self.failUnless('Advertise' in response_string)

    def testMetrics(self):
        # setup
        self.setContext(path='/')
        site_settings = Settings.objects.get_or_create(pk='1')[0]
       
        # don't return anything if no metrics specified
        response_string = metrics('', '').render(self.context)
        self.failIf(len(response_string) > 1)
        
        # render metric if metric specified
        site_settings.metrics = "Metric<br />Code"
        site_settings.save()
        self.setContext(path='/')
        response_string = metrics('', '').render(self.context)
        self.failUnless(site_settings.metrics in response_string)

    def testOnAir(self):
       pass 
