from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.template import RequestContext
from django.test import TestCase

from friends.models import Friendship

from broadcastcms.banner.models import ImageBanner
from broadcastcms.base.models import ContentBase
from broadcastcms.calendar.models import Entry
from broadcastcms.lite.models import Settings
from broadcastcms.promo.models import PromoWidget, PromoWidgetSlot
from broadcastcms.radio.models import Song
from broadcastcms.show.models import CastMember, Credit, Show
from broadcastcms.test import generate
from broadcastcms.test.mocks import RequestFactory

from widgets import Advert, NewsCompetitionsEvents, OnAir, Promotions, StatusUpdates, YourFriends

class AdvertTestCase(TestCase):
    def setContext(self, path):
        request = RequestFactory().get(path)
        self.context = RequestContext(request, {})
    
    def testRender(self):
        # setup
        self.setContext(path='/')
        site_settings = Settings.objects.get_or_create(pk='1')[0]
        private_image_banner = ImageBanner.objects.create(url='private image banner', is_public=False)
        public_image_banner = ImageBanner.objects.create(url='public image banner', is_public=True)
        widget = Advert()
       
        # if no banner is specified nothing should render
        self.failIf(widget.render(self.context))
        
        # if a private banner is specified it should not render
        site_settings.banner_section_home = [private_image_banner,]
        site_settings.save()
        self.setContext(path='/')
        self.failIf(private_image_banner.url in widget.render(self.context))
        
        # if a public banner is specified it should render
        site_settings.banner_section_home = [public_image_banner,]
        site_settings.save()
        self.setContext(path='/')
        self.failUnless(public_image_banner.url in widget.render(self.context))

        # if multiple banners are specified only 1 should render
        banners = []
        for i in range(1,5):
            banners.append(ImageBanner.objects.create(url='image banner %s' % i, is_public=True))
        site_settings.banner_section_home = banners
        site_settings.save()
        self.setContext(path='/')
        response = widget.render(self.context)

        found = 0
        for banner in banners:
            if banner.url in response:
                found += 1

        self.failIf(found != 1)

class NewsCompetitionsEventsTestCase(TestCase):
    def testEvents(self):
        generate.upcomming_events()
        events = NewsCompetitionsEvents().events

        # self.events should have no more than 3 objects
        self.failIf(len(events) > 3)

        # self.events objects should all be of type Event
        for event in events:
            self.failIf(event.classname != 'Event')
    
    def testCompetitions(self):
        generate.competitions()
        competitions = NewsCompetitionsEvents().competitions

        # self.competitions should have no more than 3 objects
        self.failIf(len(competitions) > 3)

        # self.competitions objects should all be of type Competition
        for competition in competitions:
            self.failIf(competition.classname != 'Competition')

    def testNewsPanel(self):
        generate.posts()
        news_panel = NewsCompetitionsEvents().news_panel

        # panels should only contain objects labeled 'News'
        for panel in news_panel.panels:
            for obj in panel:
                self.failUnless('News' in [label.title for label in obj.labels.all()])

    def testPanel(self):
        generate.contentbase()
        queryset = ContentBase.objects.all()[:15]
        rows_per_panel = 6

        panel = NewsCompetitionsEvents.Panel(queryset, rows_per_panel)

        # no panel should have more rows than specified by rows_per_panel.
        # in total all panels should have the same amount of objects as provided by the original queryset
        objects = []
        for p in panel.panels:
            self.failIf(len(p) > rows_per_panel)
            objects += p
        self.failIf(len(objects) != 15)

        # if we have multiple panels controls should render
        self.failUnless(panel.render_controls)
        # otherwise they shouldn't
        panel = NewsCompetitionsEvents.Panel(queryset, len(queryset))
        self.failIf(panel.render_controls)

class OnAirTestCase(TestCase):
    def setContext(self, path):
        request = RequestFactory().get(path)
        self.context = RequestContext(request, {})

    def testRender(self):
        # setup
        now = datetime.now()
        before_now = now - timedelta(minutes=10)
        after_now = now + timedelta(minutes=10)
        later = now + timedelta(minutes=60)
        much_later = now + timedelta(minutes=120)
        self.setContext(path='/')
        widget = OnAir()
        response = widget.render(self.context)

        # don't display show banner without a show
        self.failIf(response)
        
        # setup show content
        show = Show.objects.create(is_public=True)
        show_entry = Entry.objects.create(start=before_now, end=after_now, content=show, is_public=True)
        self.setContext(path='/')
        response =  widget.render(self.context)
        
        # don't display song details without a song        
        self.failIf('nowplaying' in response)
        
        # don't display listen live link if player controls are not specified in settings        
        self.failIf('listen_live' in response)
        # instead display shows link
        self.failUnless('shows' in response)
        
        # don't display studio cam link if cam image urls are not specified in settings        
        self.failIf('studio_cam' in response)
        # instead display news link
        self.failUnless('news' in response)
        
        # don't display my blog link without a castmember        
        self.failIf('my_blog' in response)
        # instead display contact link
        self.failUnless('contact' in response)

        # don't display with links if if show does not have primary castmembers
        self.failIf('with' in response)

        # setup some more content
        castmember = CastMember.objects.create(is_public=True)
        Credit.objects.create(show=show, castmember=castmember, role='1')
        later_show_entry = Entry.objects.create(start=later, end=much_later, content=show, is_public=True)
        song = Song.objects.create(is_public=True)
        song_entry = Entry.objects.create(start=before_now, end=after_now, content=song, is_public=True)
        site_settings = Settings.objects.get_or_create(pk='1')[0]
        site_settings.player_controls = "player_controls"
        site_settings.studio_cam_urls = "studio_cam_urls"
        site_settings.save()
       
        self.setContext(path='/')
        response =  widget.render(self.context)
        
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
        
        # display with links if if show has primary castmembers
        self.failUnless('with' in response)

        # display correct on air or coming up show tag
        self.failUnless('On Air' in response)
        show_entry.delete()
        response =  widget.render(self.context)
        self.failUnless('Coming Up' in response)

        
    def testGetPublicOnAirEntry(self):
        """
        get_public_on_air_entry should only return the
        first currently active public entry that has public content
        """
        # setup
        now = datetime.now()
        before_now = now - timedelta(minutes=10)
        after_now = now + timedelta(minutes=10)
        widget = OnAir()

        # don't return a current private entry, regardless of content
        content = ContentBase.objects.create(title='Content', is_public=True)
        entry = Entry.objects.create(start=before_now, end=after_now, content=content, is_public=False)
        self.failIf(entry == widget.get_public_on_air_entry(ContentBase))

        # don't return a current public entry with private content
        content = ContentBase.objects.create(title='Content', is_public=False)
        entry = Entry.objects.create(start=before_now, end=after_now, content=content, is_public=True)
        self.failIf(entry == widget.get_public_on_air_entry(ContentBase))
        
        # return a current public entry with public content
        content = ContentBase.objects.create(title='Content', is_public=True)
        entry = Entry.objects.create(start=before_now, end=after_now, content=content, is_public=True)
        self.failUnless(entry == widget.get_public_on_air_entry(ContentBase))
    
    def testGetPublicNextOnAirEntry(self):
        """
        get_public_next_on_air_entry should only return the
        first 'coming up next' active public entry that has public content
        """
        # setup
        now = datetime.now()
        later = now + timedelta(minutes=60)
        much_later = now + timedelta(minutes=120)
        widget = OnAir()

        # don't return a private entry, regardless of content
        content = ContentBase.objects.create(title='Content', is_public=True)
        entry = Entry.objects.create(start=later, end=much_later, content=content, is_public=False)
        self.failIf(entry == widget.get_public_next_on_air_entry(ContentBase))

        # don't return a public entry with private content
        content = ContentBase.objects.create(title='Content', is_public=False)
        entry = Entry.objects.create(start=later, end=much_later, content=content, is_public=True)
        self.failIf(entry == widget.get_public_next_on_air_entry(ContentBase))
        
        # return a public entry with public content
        content = ContentBase.objects.create(title='Content', is_public=True)
        entry = Entry.objects.create(start=later, end=much_later, content=content, is_public=True)
        self.failUnless(entry == widget.get_public_next_on_air_entry(ContentBase))
    
class PromotionsTestCase(TestCase):
    def setContext(self, path):
        request = RequestFactory().get(path)
        self.context = RequestContext(request, {})

    def testRender(self):
        # setup
        self.setContext(path='/')
        widget = Promotions()
        response = widget.render(self.context)
        
        # don't display anything if a promo widget is not set
        self.failIf(response)
        
        # setup promo widget
        promo_widget = PromoWidget.objects.create(title="promo widget", is_public=False)

        # setup settings
        site_settings = Settings.objects.get_or_create(pk='1')[0]
        site_settings.homepage_promo_widget = promo_widget
        site_settings.save()
        
        self.setContext(path='/')
        response = widget.render(self.context)
        
        # don't display anything for a private promo widget
        self.failIf(response)
        
        # setup content
        private_content = ContentBase.objects.create(title="private content", is_public=False)
        public_content = ContentBase.objects.create(title="public content", is_public=True)

        # setup slots
        private_slot_private_content = PromoWidgetSlot.objects.create(title="private slot private content", content=private_content, widget=promo_widget, is_public=False)
        private_slot_public_content = PromoWidgetSlot.objects.create(title="private slot public content", content=public_content, widget=promo_widget, is_public=False)
        public_slot_private_content = PromoWidgetSlot.objects.create(title="public slot private content", content=private_content, widget=promo_widget, is_public=True)
        public_slot_public_content = PromoWidgetSlot.objects.create(title="public slot public content", content=public_content, widget=promo_widget, is_public=True)

        promo_widget.is_public = True
        promo_widget.save()
        
        # gen response
        self.setContext(path='/')
        response = widget.render(self.context)

        # private slot with private content should not render
        self.failIf("private slot private content" in response)
        
        # private slot with public content should not render
        self.failIf("private slot public content" in response)
        
        # public slot with private content should not render
        self.failIf("public slot private content" in response)
       
        # public slot with public content should render
        self.failUnless("public slot public content" in response)
        
        # modelbase objects should be renderable (i.e. image banners)
        modelbase_content = ImageBanner.objects.create(title="modelbase content", is_public=True)
        slot= PromoWidgetSlot.objects.create(title="modelbase slot", content=modelbase_content, widget=promo_widget, is_public=True)
        self.setContext(path='/')
        response = widget.render(self.context)
        self.failUnless("modelbase content" in response)

class StatusUpdatesTestCase(TestCase):
    def setContext(self, path):
        request = RequestFactory().get(path)
        self.context = RequestContext(request, {})
    
    def testGetCastMemberUpdates(self):
        # setup
        generate.status_updates()
        generate.show_credits()

        # only get updates for castmembers that have credits of role 1
        updates = StatusUpdates().get_castmember_updates()
        for update in updates:
            self.failUnless(Credit.objects.filter(castmember=CastMember.objects.filter(owner=update.user)[0])[0].role == u'1')
            
        # return no more than 4 updates 
        self.failIf(len(updates) > 4)

    def testGetFriendsUpdates(self):
        # setup
        generate.status_updates()
        self.setContext('/')
        user = User.objects.create_user('admin', 'admin@admin.com', 'admin')
        user = self.context['request'].user

        # no updates should return for anonymous
        updates = StatusUpdates().get_friends_updates(user)
        self.failIf(updates)
        
        # no updates should return for authenticated users without friends
        user = authenticate(username='admin', password='admin')
        updates = StatusUpdates().get_friends_updates(user)
        self.failIf(updates)

        # updates should return for authenticated users with friends 
        generate.admin_friends()
        updates = StatusUpdates().get_friends_updates(user)
        self.failUnless(updates)

        # returned updates should be for user's friends only
        for update in updates:
            self.failUnless(Friendship.objects.are_friends(user, update.user))
        
        # return no more than 4 updates 
        self.failIf(len(updates) > 4)

    def testRender(self):
        # setup
        self.setContext('/')
        widget = StatusUpdates()

        # don't render the widget without castmember or friend updates
        response = widget.render(self.context)
        self.failIf('Update Stream' in response)

        # generate updates
        generate.status_updates()
        generate.show_credits()
        
        # render the widget if castmember or friend updates are found
        response = widget.render(self.context)
        self.failUnless('Update Stream' in response)

        # for anonymous users only render castmember updates
        self.failIf('Your Friends' in response and "DJ's" not in response)
        
        # for authenticated users without friends only render castmember updates
        user = User.objects.create_user('admin', 'admin@admin.com', 'admin')
        self.context['request'].user = authenticate(username='admin', password='admin')
        response = widget.render(self.context)
        self.failIf('Your Friends' in response and "DJ's" not in response)
        
        # for authenticated users with friends render both castmember and friend updates
        generate.admin_friends()
        response = widget.render(self.context)
        self.failUnless('Your Friends' in response and "DJ's" in response)

class YourFriendsTestCase(TestCase):
    def setContext(self, path):
        request = RequestFactory().get(path)
        self.context = RequestContext(request, {})
    
    def testRender(self):
        #setup
        self.setContext(path='/')
        user = User.objects.create_user('test', 'test@test.com', 'test')
        widget = YourFriends()

        # anonymous users receive sign in text
        response = widget.render(self.context)
        self.failUnless("Sign in to view Your Friends" in response)
        
        # authenticated users with no friends receive find friends link
        self.context['request'].user = authenticate(username='test', password='test')
        response = widget.render(self.context)
        self.failUnless("You don't have any friends. Go find some now." in response)
        
        # authenticated users with friends receive friend listing and find more friends link
        friend = User.objects.create_user('friend', 'friend@friend.com', 'friend')
        friends = Friendship.objects.create(to_user=friend, from_user=user)
        response = widget.render(self.context)
        self.failUnless('li' in response)
        self.failUnless('Find more Friends' in response)
        self.failUnless('View all Friends' in response)
