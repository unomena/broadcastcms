from math import ceil
from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.test import TestCase

from broadcastcms.banner.models import ImageBanner
from broadcastcms.event.models import Event
from broadcastcms.label.models import Label
from broadcastcms.lite.models import Settings
from broadcastcms.lite.templatetags.desktop_inclusion_tags import *
from broadcastcms.post.models import Post
from broadcastcms.show.models import CastMember, Credit, Show
from broadcastcms.test.mocks import RequestFactory

# import desktop views to execute public.site.register
import broadcastcms.lite.desktop_views

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

        # modelbase objects should be renderable (i.e. image banners)
        label = Label.objects.create(title="modelbase label", is_visible=True)
        content = ImageBanner.objects.create(title="modelbase content", is_public=True)
        content.labels.add(label)
        content.save()
        site_settings.homepage_featured_labels = []
        site_settings.homepage_featured_labels.add(label)
        site_settings.save()
        self.setContext(path='/')
        response = features('', '').render(self.context)
        self.failUnless("modelbase content" in response)

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
        later = now + timedelta(minutes=60)
        much_later = now + timedelta(minutes=120)
        self.setContext(path='/')
        response =  on_air('', '').render(self.context)

        # don't display show banner without a show     
        self.failIf(response.replace('\n', ''))
        
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
        later_show_entry = Entry.objects.create(start=later, end=much_later, content=show, is_public=True)
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

        # display correct on air or coming up show tag
        self.failUnless('On Air' in response)
        show_entry.delete()
        response =  on_air('', '').render(self.context)
        self.failUnless('Coming Up' in response)

        
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
    
    def testOnAirGetPublicNextOnAirEntry(self):
        """
        get_public_next_on_air_entry should only return the
        first 'coming up next' active public entry that has public content
        """
        # setup
        now = datetime.now()
        later = now + timedelta(minutes=60)
        much_later = now + timedelta(minutes=120)

        # don't return a private entry, regardless of content
        content = ContentBase.objects.create(title='Content', is_public=True)
        entry = Entry.objects.create(start=later, end=much_later, content=content, is_public=False)
        self.failIf(entry == on_air('', '').get_public_next_on_air_entry(ContentBase))

        # don't return a public entry with private content
        content = ContentBase.objects.create(title='Content', is_public=False)
        entry = Entry.objects.create(start=later, end=much_later, content=content, is_public=True)
        self.failIf(entry == on_air('', '').get_public_next_on_air_entry(ContentBase))
        
        # return a public entry with public content
        content = ContentBase.objects.create(title='Content', is_public=True)
        entry = Entry.objects.create(start=later, end=much_later, content=content, is_public=True)
        self.failUnless(entry == on_air('', '').get_public_next_on_air_entry(ContentBase))


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

    def testSlidingUpdatesNodeGetInstances(self):
        # setup
        update_types = ContentType.objects.all().filter(model__in=['Post', 'Event'])
        site_settings = Settings.objects.create()
        node = SlidingUpdatesNode()

        # don't return anything if no update types have been set
        self.failIf(node.get_instances(site_settings))

        # don't return anything if update types have been set without public content 
        site_settings.update_types = update_types
        site_settings.save()
        self.failIf(node.get_instances(site_settings))

        # return public instances for set update types
        # instances should be returned as their respective leaf classes
        post = Post.objects.create(is_public=True)
        event = Event.objects.create(is_public=True)
        result = node.get_instances(site_settings)
        self.failUnless(post in result and event in result)
        
        # don't return instances for non update types
        show = Show.objects.create(is_public=True)
        self.failIf(show in node.get_instances(site_settings))

        # only return as many instances as specified in count
        node.count = 5
        for i in range(0, 10):
            Post.objects.create(is_public=True)
        self.failIf(len(node.get_instances(site_settings)) > node.count)
    
    def testSlidingUpdatesNodeBuildPanels(self):
        # setup
        update_types = ContentType.objects.all().filter(model__in=['Post', 'Event'])
        site_settings = Settings.objects.create()
        node = SlidingUpdatesNode(tray_length=2, panel_rows=3, count=20)

        # panels should be empty if no content is available
        instances = node.get_instances(site_settings)
        panels = node.build_panels(instances)
        self.failIf(panels)
        
        # check if panels are formed correctly 
        site_settings.update_types = update_types
        site_settings.save()
        for i in range(0, 25):
            Post.objects.create(is_public=True)
        instances = node.get_instances(site_settings)
        panels = node.build_panels(instances)

        # no more than max possible panels as allowed by instance count, 
        max_panels = ceil(float(node.count) / (node.panel_rows * node.tray_length))
        self.failIf(len(panels) > max_panels)

        # no panels with more rows than panel_rows
        for panel in panels:
            self.failIf(len(panel) > node.panel_rows)
        
        # no trays longer than tray_length
        for panel in panels:
            for tray in panel:
                self.failIf(len(tray) > node.tray_length)

        # no tray/panel/row overlap (since we are generating a unique set
        # of instances, overlap is indicated if any tray contains content 
        # also present in any other tray
        dup_test = []
        for panel in panels:
            for tray in panel:
                for instance in tray:
                    self.failIf(instance in dup_test)
                    dup_test.append(instance)

        # all instances are accounted for in trays and are arranged in teh order 
        # they were provided
        self.failUnless(dup_test == instances)
    
    def testHomeUpdates(self):
        # setup
        update_types = ContentType.objects.all().filter(model__in=['Post', 'Event'])
        site_settings = Settings.objects.create()
        site_settings.update_types = update_types
        site_settings.save()
        self.setContext(path='/')
        
        # don't render anything if panels are empty
        self.failIf('updates' in home_updates('', '').render(self.context))

        # sliding controls should not render if only one panel is available
        for i in range(0, 2):
            Post.objects.create(is_public=True)
        self.failIf('scroll_nav' in home_updates('', '').render(self.context))

        # sliding controls should render if more than one panel is available
        for i in range(0, 25):
            Post.objects.create(is_public=True)
        self.failUnless('scroll_nav' in home_updates('', '').render(self.context))
