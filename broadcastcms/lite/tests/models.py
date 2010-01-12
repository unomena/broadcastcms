from django.template import RequestContext
from django.test import TestCase

from broadcastcms.banner.models import ImageBanner
from broadcastcms.lite.context_processors import SITE_SECTIONS
from broadcastcms.lite.models import Settings
from broadcastcms.test.mocks import RequestFactory

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
            b = getattr(site_settings, 'banner_section_%s' % section)
            b.clear()
            for banner in banners:
                b.add(banner)
            site_settings.save()
            self.setContext(path=section)
            # only public banners are returned by default
            self.failUnless(banners[1:] == site_settings.get_section_banners(self.context['section']))
            # but if specified both private and public banners are returned
            self.failUnless(banners == site_settings.get_section_banners(self.context['section'], permitted=False))
