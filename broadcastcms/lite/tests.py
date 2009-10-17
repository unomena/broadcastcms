import unittest
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.template import RequestContext
from django.test.client import Client
from django.test import TestCase

from broadcastcms.banner.models import ImageBanner
from broadcastcms.base.models import ContentBase
from broadcastcms.label.models import Label
from broadcastcms.show.models import CastMember, Credit, Show
from broadcastcms.test.mocks import RequestFactory

from context_processors import SITE_SECTIONS
from models import Settings
from templatetags.desktop_inclusion_tags import *

# import desktop views to register content views
import desktop_views

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


class ModelsTestCase(TestCase):
    def setContext(self, path):
        request = RequestFactory().get(path)
        self.context = RequestContext(request, {})
    
    def testSettingsGetSectionBanners(self):
        self.setContext(path='/')
        site_settings = Settings.objects.create()

        # if no banners are specified return nothing for each section
        for section in SITE_SECTIONS:
            self.setContext(path=section)
            self.failIf(site_settings.get_section_banners(self.context['section']))

        # if banners are specified return the correct ones for each section
        # banners should be returned as their respective leaf classes
        for section in SITE_SECTIONS:
            banners = [
                ImageBanner.objects.create(url='private %s image banner' % section, is_public=False), 
                ImageBanner.objects.create(url='public %s image banner' % section, is_public=True),
            ]
            setattr(site_settings, 'banner_section_%s' % section, banners)
            site_settings.save()
            self.setContext(path=section)
            # only public banners are returned by default
            self.failUnless(banners[1:] == site_settings.get_section_banners(self.context['section']))
            # but if specified both private and public banners are returned
            self.failUnless(banners == site_settings.get_section_banners(self.context['section'], permitted=False))


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

        # check that the home template is used
        self.assertTemplateUsed(response, 'desktop/content/home.html')
        
        # check that skeleton templates are used
        self.assertSkeletonTemplatesUsed(response)

        # check that correct inclusion tag templates are used
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/home/features.html')
        self.assertTemplateUsed(response, 'desktop/inclusion_tags/home/on_air.html')


class DesktopInclusionTagsTestCase(TestCase):
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

    def testFeatures(self):
        #setup labels
        contentless_label = Label.objects.create(title="contentless label", is_visible=True)
        private_content_label = Label.objects.create(title="private content label", is_visible=True)
        visible_label = Label.objects.create(title="visible label", is_visible=True)
        invisible_label = Label.objects.create(title="invisible label", is_visible=False)
        
        #setup content
        private_content = ContentBase.objects.create(title="private content", is_public=False)
        private_content.labels= [private_content_label,visible_label]
        private_content.save()
        public_content = ContentBase.objects.create(title="public content", is_public=True)
        public_content.labels = [visible_label, invisible_label,]
        public_content.save()
        
        # setup settings
        site_settings = Settings.objects.get_or_create(pk='1')[0]
        site_settings.homepage_featured_labels = [contentless_label, private_content_label, invisible_label, visible_label]
        site_settings.save()
        self.setContext(path='/')
        response = features('', '').render(self.context)
        
        # labels with no content should not render
        self.failIf(contentless_label.title in response)
        
        # labels with private content should not render
        self.failIf(private_content_label.title in response)
        
        # invisible labels should not render, even if they have public content
        self.failIf(invisible_label.title in response)
        
        # visible labels with public content should render
        self.failUnless(visible_label.title in response)

        # private content should not render
        self.failIf(private_content.title in response)
        
        # public content should render
        self.failUnless(public_content.title in response)

        # maximum of 3 labels should render
        site_settings.homepage_featured_labels = []
        for i in range(1,5):
            label = Label.objects.create(title="label %s" % i, is_visible=True)
            public_content.labels.add(label)
            site_settings.homepage_featured_labels.add(label)
        public_content.save()
        site_settings.save()
        self.setContext(path='/')
        response = features('', '').render(self.context)
        self.failIf("label 4" in response)

    def testHomeAdvert(self):
        # setup
        self.setContext(path='/')
        site_settings = Settings.objects.get_or_create(pk='1')[0]
        private_image_banner = ImageBanner.objects.create(url='private image banner', is_public=False)
        public_image_banner = ImageBanner.objects.create(url='public image banner', is_public=True)
       
        # if no banner is specified nothing should render
        self.failIf(home_advert('', '').render(self.context))
        
        # if a private banner is specified it should not render
        site_settings.banner_section_home = [private_image_banner,]
        site_settings.save()
        self.setContext(path='/')
        self.failIf(private_image_banner.url in home_advert('', '').render(self.context))
        
        # if a public banner is specified it should render
        site_settings.banner_section_home = [public_image_banner,]
        site_settings.save()
        self.setContext(path='/')
        self.failUnless(public_image_banner.url in home_advert('', '').render(self.context))

        # if multiple banners are specified only 1 should render
        banners = []
        for i in range(1,5):
            banners.append(ImageBanner.objects.create(url='image banner %s' % i, is_public=True))
        site_settings.banner_section_home = banners
        site_settings.save()
        self.setContext(path='/')
        response = home_advert('', '').render(self.context)

        found = 0
        for banner in banners:
            if banner.url in response:
                found += 1

        self.failIf(found != 1)
        
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
        # setup
        now = datetime.now()
        before_now = now - timedelta(minutes=10)
        after_now = now + timedelta(minutes=10)
        self.setContext(path='/')
        response =  on_air('', '').render(self.context)

        # don't display show banner without a show        
        self.failIf('banner_thumb' in response)
        
        # don't display show details without a show        
        self.failIf('showtitle' in response)
        
        # don't display song details without a song        
        self.failIf('nowplaying' in response)
        
        # don't display listen live link if player controls are not specified in settings        
        self.failIf('listen_live' in response)
        
        # don't display studio cam link if cam image urls are not specified in settings        
        self.failIf('studio_cam' in response)
        
        # don't display my blog link without a castmember        
        self.failIf('my_blog' in response)

        # setup some content
        show = Show.objects.create(is_public=True)
        castmember = CastMember.objects.create(is_public=True)
        Credit.objects.create(show=show, castmember=castmember)
        show_entry = Entry.objects.create(start=before_now, end=after_now, content=show, is_public=True)
        song = Song.objects.create(is_public=True)
        song_entry = Entry.objects.create(start=before_now, end=after_now, content=song, is_public=True)
        site_settings = Settings.objects.get_or_create(pk='1')[0]
        site_settings.player_controls = "player_controls"
        site_settings.studio_cam_urls = "studio_cam_urls"
        site_settings.save()
       
        self.setContext(path='/')
        response =  on_air('', '').render(self.context)
        
        # display show banner for a show        
        self.failUnless('banner_thumb' in response)
        
        # display show details for a show        
        self.failUnless('showtitle' in response)
        
        # display song details for a song        
        self.failUnless('nowplaying' in response)
        
        # display listen live link if player controls are specified in settings        
        self.failUnless('listen_live' in response)
        
        # display studio cam link if cam image urls are specified in settings        
        self.failUnless('studio_cam' in response)
        
        # display my blog link for a castmember        
        self.failUnless('my_blog' in response)
        


    def testOnAirGetPublicOnAirEntry(self):
        """
        get_public_on_air_entry should only return the
        first currently active public entry that has public content
        """
        # setup
        now = datetime.now()
        before_now = now - timedelta(minutes=10)
        after_now = now + timedelta(minutes=10)

        # don't return a current private entry, regardless of content
        content = ContentBase.objects.create(title='Content', is_public=True)
        entry = Entry.objects.create(start=before_now, end=after_now, content=content, is_public=False)
        self.failIf(entry == on_air('', '').get_public_on_air_entry(ContentBase))

        # don't return a current public entry with private content
        content = ContentBase.objects.create(title='Content', is_public=False)
        entry = Entry.objects.create(start=before_now, end=after_now, content=content, is_public=True)
        self.failIf(entry == on_air('', '').get_public_on_air_entry(ContentBase))
        
        # return a current public entry with public content
        content = ContentBase.objects.create(title='Content', is_public=True)
        entry = Entry.objects.create(start=before_now, end=after_now, content=content, is_public=True)
        self.failUnless(entry == on_air('', '').get_public_on_air_entry(ContentBase))

    def testOnAirGetPrimaryCastmember(self):
        """
        get_primary_castmember should only return the most seniour (based on role)
        public castmember for the given show
        """
        # setup
        show = Show.objects.create()

        # don't retun anything if the show does not have credits 
        self.failIf(on_air('', '').get_primary_castmember(show))

        # don't return anything if the show does not have any public credits
        castmember = CastMember.objects.create(is_public=False)
        credit = Credit.objects.create(show=show, castmember=castmember)
        self.failIf(on_air('', '').get_primary_castmember(show))

        # expect a response if the show has credits with public castmembers
        castmember = CastMember.objects.create(is_public=True)
        credit = Credit.objects.create(show=show, castmember=castmember)
        self.failUnless(on_air('', '').get_primary_castmember(show))
        
        # return the primary public castmember
        show = Show.objects.create()
        primary_private_castmember = CastMember.objects.create(is_public=False)
        primary_public_castmember = CastMember.objects.create(is_public=True)
        secondary_castmember = CastMember.objects.create(is_public=True)
        Credit.objects.create(show=show, castmember=primary_private_castmember, role=1)
        Credit.objects.create(show=show, castmember=primary_public_castmember, role=2)
        Credit.objects.create(show=show, castmember=secondary_castmember, role=3)
        primary_castmember = on_air('', '').get_primary_castmember(show)
        self.failIf(primary_private_castmember == primary_castmember)
        self.failIf(secondary_castmember == primary_castmember)
        self.failUnless(primary_public_castmember == primary_castmember)
