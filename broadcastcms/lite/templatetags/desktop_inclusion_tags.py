from datetime import datetime

from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from user_messages.models import Thread
from friends.models import Friendship

from broadcastcms.calendar.models import Entry
from broadcastcms.competition.models import Competition
from broadcastcms.event.models import Event
from broadcastcms.label.models import Label
from broadcastcms.show.models import Credit, Show
from broadcastcms.base.models import ContentBase, ModelBase
from broadcastcms.radio.models import Song
from broadcastcms.cache.decorators import cache_view_function
from broadcastcms.status.models import StatusUpdate
from broadcastcms.widgets.utils import SSIContentResolver

register = template.Library()

# Skeleton

@register.tag
def account_links(parser, token):
    return AccountLinksNode()

class AccountLinksNode(SSIContentResolver, template.Node):
    user_unique = True

    #@cache_view_function(10*60, respect_user=True)
    def render_content(self, context):
        """
        Renders anonymous avatar, sign in and sign up links for anonymous users.
        Renders avatar, messages and sign out links for authenticated users.
        """
        request = context['request']

        # get user and profile objects
        user = getattr(request, 'user', None)
        if user.is_authenticated():
        
            # get unread message count
            messages = Thread.objects.unread(user).count()
            username = user.username
            limited_username = "%s..." % username[:10] if len(username) > 10 else username
       
            context.update({
                'user': user,
                'limited_username': limited_username,
                'fb_authenticated': request.facebook.check_session(request),
                'messages': messages,
            })
            
        return render_to_string('desktop/inclusion_tags/skeleton/account_links.html', context)

    def get_ssi_url(self, request):
        return reverse('ssi_account_links_node')

@register.tag
def masthead(parser, token):
    return MastheadNode()

class MastheadNode(template.Node):
    @cache_view_function(10*60, respect_user=True, respect_path=True)
    def render(self, context):
        """
        Renders the sitewide masthead, including site logo, site section links, search and account links.
        Site section links are highlighted when on appropriate section.
        """
        section = context['section']
        items = [
            {'title': 'Home', 'url': reverse('home'), 'current': section == 'home'},
            {'title': 'Shows', 'url': reverse('shows_line_up'), 'current': section == 'shows'},
            {'title': 'Chart', 'url': reverse('chart'), 'current': section == 'chart'},
            {'title': 'Win', 'url': reverse('competitions'), 'current': section == 'competitions'},
            {'title': 'News', 'url': reverse('news'), 'current': section == 'news'},
            {'title': 'Events', 'url': reverse('events'), 'current': section == 'events'},
            {'title': 'Galleries', 'url': reverse('galleries'), 'current': section == 'galleries'},
            {'title': 'Reviews', 'url': reverse('reviews'), 'current': section == 'reviews'},
        ]
   
        context.update({
            'items': items,
        })

        return render_to_string('desktop/inclusion_tags/skeleton/masthead.html', context)

@register.tag
def mastfoot(parser, token):
    return MastfootNode()

class MastfootNode(template.Node):
    @cache_view_function(10*60, respect_user=True)
    def render(self, context):
        """
        Renders the sitewide footer.
        Copyright Year is rendered dynamically.
        Mobile version link is rendered only when settings.MOBILE_HOSTNAME has been defined.
        T&C, Privacy Policy, About Us and Advertise links are 
        rendered only when appropriate content has been provided in site settings object.
        """
        site_settings = context['settings']
        terms = site_settings.terms
        privacy = site_settings.privacy
        about = site_settings.about
        advertise = site_settings.advertise
        
        # standard site section items to display in the footer navcard
        sitemap_items = [
            {'title': 'Home', 'url': reverse('home')},
            {'title': 'Shows &amp; DJs', 'url': reverse('shows_line_up')},
            {'title': 'Listen Live', 'url': "javascript: openPlayer(%s);" % reverse('listen_live')},
            {'title': 'Music Chart', 'url': reverse('chart')},
            {'title': 'Competitions', 'url': reverse('competitions')},
            {'title': 'News Updates', 'url': reverse('news')},
            {'title': 'Events Calendar', 'url': reverse('events')},
            {'title': 'Contact Us', 'url': reverse('contact')},
        ]

        # append additional dynamic navcard items
        if about: sitemap_items.append({'title': "About Us", 'url': reverse('info_content', kwargs={'section': "about"})})
        if advertise: sitemap_items.append({'title': "Advertise", 'url': reverse('info_content', kwargs={'section': "advertise"})})
        
        # arrange items into easily rendered columns
        sitemap_columns = []
        rows = 3
        slices = range(0, len(sitemap_items), rows)
        for slice_start in slices:
            sitemap_columns.append(sitemap_items[slice_start: slice_start + rows])

        # build the mobile url from settings.MOBILE_HOSTNAME
        mobile_hostname = getattr(settings, 'MOBILE_HOSTNAME', None)
        mobile_url = 'http://%s' % mobile_hostname if mobile_hostname else None

        context = {
            'terms': terms,
            'privacy': privacy,
            'terms_and_privacy': (terms and privacy),
            'terms_or_privacy': (terms or privacy),
            'sitemap_columns': sitemap_columns,
            'mobile_url': mobile_url,
        }
        return render_to_string('desktop/inclusion_tags/skeleton/mastfoot.html', context)

@register.tag
def mastfoot_popup(parser, token):
    return MastfootPopupNode()

class MastfootPopupNode(template.Node):
    def render(self, context):
        """
        Renders the popup footer.
        Copyright Year is rendered dynamically.
        Mobile version link is rendered only when settings.MOBILE_HOSTNAME has been defined.
        T&C, Privacy Policy, links are rendered only when appropriate content has been provided
        in site settings object.
        """
        site_settings = context['settings']
        terms = site_settings.terms
        privacy = site_settings.privacy
        
        # build the mobile url from settings.MOBILE_HOSTNAME
        mobile_hostname = getattr(settings, 'MOBILE_HOSTNAME', None)
        mobile_url = 'http://%s' % mobile_hostname if mobile_hostname else None

        context = {
            'terms': terms,
            'privacy': privacy,
            'terms_and_privacy': (terms and privacy),
            'terms_or_privacy': (terms or privacy),
            'mobile_url': mobile_url,
        }
        return render_to_string('desktop/inclusion_tags/skeleton/mastfoot.html', context)

@register.tag
def metrics(parser, token):
    return MetricsNode()

class MetricsNode(template.Node):
    def render(self, context):
        settings = context['settings']
        metrics = settings.metrics
        context = {
            'metrics': settings.metrics,
        }
        return render_to_string('desktop/inclusion_tags/skeleton/metrics.html', context)

# Home

@register.tag
def home_advert(parser, token):
    return HomeAdvertNode()

class HomeAdvertNode(template.Node):
    @cache_view_function(10*60)
    def render(self, context):
        """
        Render a single advertising banner as specified in the Settings 
        object's banner section home field. Only public banners are rendered
        """
        section = context['section']
        settings = context['settings']
        banners = settings.get_section_banners(section)
        return banners[0].render() if banners else ""

@register.tag
def home_friends(parser, token):
    return HomeFriendsNode()

class HomeFriendsNode(template.Node):
    def render(self, context):
        request = context['request']
        user = request.user
       
        if user.is_authenticated():
            friends = Friendship.objects.friends_for_user(user)
            friends_count = len(friends)
            friends = [friend['friend'] for friend in friends][:10]
    
            context.update({
                'friends': friends,
                'friends_count': friends_count
            })

        return render_to_string('desktop/inclusion_tags/home/friends.html', context)

@register.tag
def home_status_updates(parser, token):
    return HomeStatusUpdatesNode()

class HomeStatusUpdatesNode(template.Node):
    def render(self, context):
        request = context['request']
        user = request.user
      
        credits = Credit.objects.all()
        credits = Credit.objects.filter(role='1', show__in=Show.permitted.all).select_related('castmember')
        castmember_owners = [credit.castmember.owner for credit in credits]

        castmember_status_updates = StatusUpdate.objects.filter(user__in=castmember_owners).select_related('user').order_by('-timestamp')[:4]

        current = None
        friends_status_updates = []
        if user.is_authenticated():
            friends = Friendship.objects.friends_for_user(user)
            friends = [friend['friend'] for friend in friends]
            friends_status_updates = StatusUpdate.objects.filter(user__in=friends).select_related('user').order_by('-timestamp')[:4]

            current = StatusUpdate.objects.current_status(user)

        context.update({
            'castmember_status_updates': castmember_status_updates,
            'friends_status_updates': friends_status_updates,
            'current': current,
        })

        return render_to_string('desktop/inclusion_tags/home/status_updates.html', context)

@register.tag
def features(parser, token):
    return FeaturesNode()

class FeaturesNode(template.Node):
    @cache_view_function(10*60)
    def render(self, context):
        """
        Renders the homepage features box. 
        Content is featured through a PromoWidget, which is specified 
        in the setting object's 'homepage promo widget' field.
        Only public content will render.
        Returns an empty string if no sutiable content is found to render.
        """
        # grab promo widget from settings
        settings = context['settings']
        promo_widget = settings.homepage_promo_widget
        # only public promo widget with public slots containing public content qualify as valid items
        if promo_widget:
            if promo_widget.is_public:
                slots = promo_widget.promowidgetslot_set.permitted()
                if slots:
                    items = []
                    for slot in slots:
                        content = slot.content
                        if content.is_public:
                            content = content.as_leaf_class()
                            # grab item url from view method or property
                            try:
                                url = content.url(context)
                            except TypeError:
                                url = content.url
                            items.append({
                                'title': slot.title,
                                'content': content,
                                'url': url,
                            })

                    if items: 
                        context = {
                            'items': items
                        }
                        return render_to_string('desktop/inclusion_tags/home/features.html', context)
        return ''

@register.tag
def on_air(parser, token):
    return OnAirNode()

class OnAirNode(template.Node):
    def get_public_on_air_entry(self, content_type):
        """
        Returns first currently active public entry that has public content
        """
        entries = Entry.objects.permitted().by_content_type(content_type).now().filter(content__is_public=True)
        return entries[0] if entries else None
    
    def get_public_next_on_air_entry(self, content_type):
        """
        Returns first 'coming up next' public entry that has public content
        """
        entries = Entry.objects.permitted().by_content_type(content_type).upcoming().filter(content__is_public=True)
        return entries[0] if entries else None

    @cache_view_function(2*60)
    def render(self, context):
        """
        Renders the homepage On Air box containing details on the
        current or upcoming show and current song as well as listen live, studio
        cam and castmember blog links.
        Returns an empty string if no show is found.
        """
        # get a show to display, either currently on air or coming up
        on_air = True
        show_entry = self.get_public_on_air_entry(Show)
        if not show_entry:
            show_entry = self.get_public_next_on_air_entry(Show)
            on_air = False
        show = show_entry.content.as_leaf_class() if show_entry else None
      
        if show:
            # get the primary castmember for the current on air show
            primary_castmembers = show.primary_castmembers
            primary_castmember = primary_castmembers[0] if primary_castmembers else None
            
            # build the nice with string linking to each castmembers blog
            with_str = " & ".join(['<a href="%s">%s</a>' % (castmember.url(), castmember.title) for castmember in primary_castmembers])
        
            # get the current playing song and artist info
            song_entry = self.get_public_on_air_entry(Song)
            song = song_entry.content.as_leaf_class() if song_entry else None
            artist = song.credits.all().filter(artist__is_public=True).order_by('role') if song else None

            context.update({
                'entry': show_entry,
                'show': show,
                'on_air': on_air,
                'with_str': with_str,
                'primary_castmember': primary_castmember,
                'song': song,
                'artist': artist,
            })
            return render_to_string('desktop/inclusion_tags/home/on_air.html', context)
        else:
            return ''

@register.tag
def home_news(parser, token):
    news_labels = Label.objects.filter(title__iexact="news")
    queryset = ContentBase.permitted.filter(labels__in=news_labels).order_by("-created")[:18]
    more_url = reverse('news')
    return UpdatesNode(queryset, rows_per_panel=6, node_class="updates pink", heading="Latest News", more_url=more_url)

@register.tag
def home_competitions(parser, token):
    queryset = Competition.permitted.order_by("-created")[:3]
    more_url = reverse('competitions')
    return UpdatesNode(queryset, rows_per_panel=3, node_class="updates align-right events yellow", heading="Competitions", more_url=more_url, show_images=False)

@register.tag
def home_events(parser, token):
    queryset = []
    entries = Entry.objects.permitted().upcoming().by_content_type(Event).order_by('start')
    if entries:
        for entry in entries:
            content = entry.content
            if content not in queryset:
                queryset.append(content)

    queryset = queryset[:3]
    more_url = reverse('events')
    return UpdatesNode(queryset, rows_per_panel=3, node_class="updates align-right events blue", heading="Events", more_url=more_url, show_images=False)

class UpdatesNode(template.Node):
    def __init__(self, queryset, rows_per_panel, node_class, heading, more_url, show_images=True):
        self.queryset = queryset
        self.rows_per_panel = rows_per_panel
        self.node_class = node_class
        self.heading = heading
        self.more_url = more_url
        self.show_images = show_images
    
    def build_panels(self):
        """
        Returns panels containing objects. Pannels are build according
        to the number of rows per panel requested and the number of objects in the queryset.
        """
        object_list = list(self.queryset)
        object_list_count = len(object_list)
        
        panels = []
        if object_list_count > 0:
            # generate instance slice offsets from which to populate panels
            slices = range(0, object_list_count, self.rows_per_panel)
            # populate panels based on instance slices
            for slice_start in slices:
                panels.append(object_list[slice_start: slice_start + self.rows_per_panel])

        return panels

    @cache_view_function(10*60, respect_path=True, respect_self_attrs=['heading',])
    def render(self, context):
        panels = self.build_panels()
        context = {
            'panels': panels,
            'render_controls': (len(panels) > 1),
            'node': self,
            'section': context['section'],
        }
        return render_to_string('desktop/inclusion_tags/misc/updates.html', context)

class SlidingUpdatesNode(template.Node):
    def __init__(self, tray_length=3, panel_rows=2, count=18):
        self.tray_length = tray_length
        self.panel_rows = panel_rows
        self.count = count
        super(SlidingUpdatesNode, self).__init__()

    def get_instances(self, settings):
        """
        Returns public instance for those types specified in the Settings object's
        update_types field, sorted on created date descending. The number of items returned
        is limited to the value of self.count.
        """
        # get the update types from settings
        update_types = [update_type.model_class().__name__ for update_type in settings.update_types.all()]

        # collect public instances, limited to count, sorted on created descending
        instances = ContentBase.permitted.filter(classname__in=update_types).order_by("-created")[:self.count]
        
        # return list of instance leaves
        return [instance.as_leaf_class() for instance in instances]
  
    def build_panels(self, instances):
        """
        Returns panels with trays containing instances. Pannels are build according
        to self.tray_length and self.panel_rows. Panels can be seen as pages, with 
        tray length indicating how many instances are contained in a panel row.
        """
        trays = []
        # generate instance slice offsets from which to populate trays
        slices = range(0, len(instances), self.tray_length)
        # populate trays based on instance slices
        for slice_start in slices:
            trays.append(instances[slice_start: slice_start + self.tray_length])

        panels = []
        # generate tray slice offsets
        slices = range(0, len(trays), self.panel_rows)
        # populate pannels based on tray slices
        for slice_start in slices:
            panels.append(trays[slice_start: slice_start + self.panel_rows])

        return panels

    @cache_view_function(10*60, respect_path=True)
    def render(self, context):
        """
        Renders update box containing sliding panels, which contain
        a number of trays/rows, which in turn contains latest content
        for content types specified in the Settings object's 
        update_types field. If we only one panel, sliding and sliding 
        controls are disabled.
        """
        instances = self.get_instances(context['settings'])
        panels = self.build_panels(instances)
      
        context.update({
            'panels': panels,
            'render_controls': (len(panels) > 1),
        })
        return render_to_string('desktop/inclusion_tags/misc/updates.html', context)

@register.tag
def home_updates(parser, token):
    return SlidingUpdatesNode(tray_length=3, panel_rows=2, count=18)

@register.tag
def popup_updates(parser, token):
    return SlidingUpdatesNode(tray_length=1, panel_rows=3, count=9)

@register.tag
def modal_updates(parser, token):
    return SlidingUpdatesNode(tray_length=2, panel_rows=1, count=2)

# Misc

@register.tag
def status_update(parser, token):
    return StatusUpdateNode()

class StatusUpdateNode(SSIContentResolver, template.Node):
    user_unique = True
    
    def get_ssi_url(self, request):
        return reverse('ssi_status_update_node')

    def render_content(self, context):
        """
        Return status update form for authenticated users,
        auth_reload span for anonymous.
        """
        return render_to_string('desktop/inclusion_tags/skeleton/status_update.html', context)

@register.tag
def paging(parser, token):
    token = token.split_contents()
    if not len(token) == 2:
        raise template.TemplateSytaxError, '%r tag requires exactly 1 argument.' % token[0]
    return PagingNode(token[1])


class PagingNode(template.Node):
    def __init__(self, page):
        self.page = template.Variable(page)

    def render(self, context):
        page = self.page.resolve(context)

        if page.has_other_pages():
           
            page_range = pager_items = page.paginator.page_range
            pager_item_count = 7
            middle = pager_item_count  / 2

            page_number_index = page_range.index(page.number)
            start_index = page_number_index - middle
            if start_index < 0:
                start_index = 0
            end_index = start_index + pager_item_count
            
            if end_index >= len(page_range):
                end_index = len(page_range)
                start_index = end_index - pager_item_count

            pager_items = page.paginator.page_range[start_index: end_index]
            render_first = 1 not in pager_items
            render_last = page.paginator.num_pages not in pager_items
        
            context.update({
                'page': page,
                'pager_items': pager_items,
                'render_first': render_first,
                'render_last': render_last,
            })
            return render_to_string('desktop/inclusion_tags/misc/paging.html', context)
        return ''

@register.tag
def social_paging(parser, token):
    token = token.split_contents()
    if not len(token) == 2:
        raise template.TemplateSytaxError, '%r tag requires exactly 1 argument.' % token[0]
    return SocialPagingNode(token[1])


class SocialPagingNode(template.Node):
    def __init__(self, page_obj):
        self.page_obj = template.Variable(page_obj)

    def render(self, context):
        page_obj = self.page_obj.resolve(context)
        context = {
            'request': context['request'],
            'page_obj': page_obj
        }
        return render_to_string('desktop/inclusion_tags/misc/social_paging.html', context)

@register.tag
def likes_stamp(parser, token):
    try:
        tag_name, obj_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s requires exactly 1 argument" % token.contents
    
    obj = template.Variable(obj_name)
    return LikesStampNode(obj)

class LikesStampNode(template.Node):
    def __init__(self, obj):
        self.obj = obj

    def render(self, context):
        instance = self.obj.resolve(context)
        
        # create voting url
        vote_url = reverse('xmlhttprequest_vote_on_object', kwargs={'slug': instance.slug})

        # get site name
        current_site = Site.objects.get_current()
        site_name = current_site.name
        
        context = {
            'user': context['request'].user, 
            'instance': instance,
            'vote_url': vote_url,
            'site_name': site_name,
        }
        return render_to_string('desktop/inclusion_tags/misc/likes_stamp.html', context)

@register.tag
def comments(parser, token):
    tag, instance = token.split_contents()
    return CommentsNode(instance)

class CommentsNode(template.Node):
    def __init__(self, instance):
        self.instance = template.Variable(instance)
    
    def render(self, context):
        instance = self.instance.resolve(context)
        context.update({
            'instance': instance,
        })
        return render_to_string('desktop/inclusion_tags/misc/comments.html', context)

@register.tag
def sorting(parser, token):
    token = token.split_contents()
    if not len(token) == 2:
        raise template.TemplateSytaxError, '%r tag requires exactly 1 argument.' % token[0]
    return SortingNode(token[1])


class SortingNode(template.Node):
    def __init__(self, sorter):
        self.sorter = template.Variable(sorter)

    def render(self, context):
        sorter = self.sorter.resolve(context)
        context.update({
            'self': sorter,
        })
        return render_to_string('desktop/inclusion_tags/misc/sorting.html', context)

@register.tag
def account_side_nav(parser, token):
    return AccountSideNavNode()

class AccountSideNavNode(template.Node):
    def render(self, context):
        request = context['request']
        account_section = request.path.split('/')[2]
        account_sub_section = request.path.split('/')[3]
        
        items = {'settings': 
            [{
                'title': 'My Details',
                'section': 'details',
                'class': 'my_details',
                'url': reverse('account_settings_details'),
            },
            {
                'title': 'Profile Image',
                'section': 'image',
                'class': 'profile_image',
                'url': reverse('account_settings_image'),
            },
            {
                'title': 'Subscription Settings',
                'section': 'subscriptions',
                'class': 'sub_settings',
                'url': reverse('account_settings_subscriptions'),
            },
            # XXX: Facebook Connect
            #{
            #    'title': 'Facebook Connect',
            #    'section': 'facebook',
            #    'class': 'facebook_connect',
            #},
        ],
        'friends': [{
                'title': 'My Friends',
                'section': 'my',
                'class': 'see_my_friends',
                'url': reverse('account_friends_my'),
            },
            {
                'title': "See My Friends' Recent Activity",
                'section': 'activity',
                'class': 'friends_activity',
                'url': reverse('account_friends_activity_all'),
            },
            {
                'title': "Find More Friends",
                'section': 'find',
                'class': 'more_friends',
                'url': reverse('account_friends_find'),
            },
        ]}

        titles = {
            'settings': 'Update Your Settings',
            'friends': 'Follow Your Friends',
        }
        
        context = {
            'items': items[account_section],
            'active_section': account_sub_section,
            'title': titles[account_section],
        }
        return render_to_string('desktop/inclusion_tags/account/side_nav.html', context)

@register.tag
def account_menu(parser, token):
    return AccountMenuNode()

class AccountMenuNode(template.Node):
    def render(self, context):
        request = context['request']
        
        messages = Thread.objects.unread(request.user).count()
        msg = "Messages"
        if messages:
            msg += " (%s)" % messages

        menu_items = [
            {
                'title': msg,
                'section': 'messages',
                'url': reverse('messages_inbox'),
            },
            {
                'title': 'History',
                'section': 'history',
                'url': reverse('account_history'),
            },
            {
                'title': 'Friends',
                'section': 'friends',
                'url': reverse('account_friends_my'),
            },
            {
                'title': 'Settings',
                'section': 'settings',
                'url': reverse('account_settings_details'),
            },
        ]
        account_section = request.path.split('/')[2]
       
        profile = request.user.profile

        context.update({
            'menu_items': menu_items,
            'account_section': account_section,
            'profile': profile,
        })
        return render_to_string('desktop/inclusion_tags/account/menu.html', context)

@register.tag
def account_messages_menu(parser, token):
    return AccountMessagesMenuNode()

class AccountMessagesMenuNode(template.Node):
    def render(self, context):
        request = context['request']
        
        items = [
            {
                'title': 'Inbox',
                'section': 'inbox',
                'url': reverse('messages_inbox'),
            },
            {
                'title': 'Sent',
                'section': 'sent',
                'url': reverse('messages_sent'),
            },
            {
                'title': 'New Message',
                'section': 'create',
                'class': 'compose',
                'url': reverse('message_create'),
            },
        ]
        section = request.path.split('/')[3]

        context = {
            'items': items,
            'section': section,
        }
        return render_to_string('desktop/inclusion_tags/account/sub_menu.html', context)

@register.tag
def account_friends_find_menu(parser, token):
    return AccountFriendsFindMenuNode()

class AccountFriendsFindMenuNode(template.Node):
    def render(self, context):
        request = context['request']
        
        items = [
            {
                'title': 'Find People You Know',
                'section': 'find',
                'url': reverse('account_friends_find'),
            },
        ]

        if request.facebook.check_session(request):
            items.append({
                'title': 'Invite Facebook Friends',
                'section': 'facebook',
                'url': reverse('account_friends_facebook_invite'),
            })

        section = request.path.split('/')[-2]

        context = {
            'items': items,
            'section': section,
        }
        return render_to_string('desktop/inclusion_tags/account/sub_menu.html', context)

@register.tag
def account_thanks(parser, token):
    return AccountThanksNode()

class AccountThanksNode(template.Node):
    def render(self, context):
        try:
            if context['form'].is_valid():
                return render_to_string('desktop/inclusion_tags/account/thanks.html', context)
        except:
            pass
        return ''

# Widgets

@register.tag
def advert(parser, token):
    return AdvertNode()

class AdvertNode(template.Node):
    @cache_view_function(10*60, respect_path=True)
    def render(self, context):
        section = context['section']
        settings = context['settings']
        banners = settings.get_section_banners(section)
        context = {
            'banners': banners,
        }
        return render_to_string('desktop/inclusion_tags/widgets/advert.html', context)


@register.tag
def now_playing(parser, token):
    return NowPlayingNode()

class NowPlayingNode(OnAirNode):  
    def get_next_entry(self, content_type):
        valid_entry = None
        now = datetime.now()
        
        entries = Entry.objects.permitted().by_content_type(content_type).filter(start__gt=now).order_by('start')
        for entry in entries:
            if entry.content.is_public:
                valid_entry = entry
                break

        return valid_entry

    @cache_view_function(2*60)
    def render(self, context):
        # get the current on air show
        show_entry = self.get_public_on_air_entry(Show)
        show = show_entry.content.as_leaf_class() if show_entry else None
       
        # get the primary castmember for the current on air show
        primary_castmembers = show.primary_castmembers if show else None
        primary_castmember = primary_castmembers[0] if primary_castmembers else None
        
        # get the current playing song and artist info
        song_entry = self.get_public_on_air_entry(Song)
        song = song_entry.content.as_leaf_class() if song_entry else None
        artist = song.get_primary_artist() if song else None
        
        next_entry = self.get_next_entry(Show)
        next_show = next_entry.content.as_leaf_class() if next_entry else None
        next_castmembers = next_show.primary_castmembers if next_show else None
        next_castmember = next_castmembers[0] if next_castmembers else None
        next_str = "%s%s" % (next_show.title, " with %s" % next_castmember.title if next_castmember else "") if next_show else ''
        next_str = next_str[:40] + ' ...' if len(next_str) > 40 else next_str
        context.update({
            'entry': show_entry,
            'show': show,
            'primary_castmember': primary_castmember,
            'song': song,
            'artist': artist,
            'next_str': next_str,
        })
        return render_to_string('desktop/inclusion_tags/widgets/now_playing.html', context)

"""
@register.tag
def updates(parser, token):
    return UpdatesNode()

class UpdatesNode(SlidingUpdatesNode):
        
    @cache_view_function(10*60)
    def render(self, context):
        instances = [instance.as_leaf_class() for instance in self.get_instances(context['settings'])[:5]]
        context.update({
            'instances': instances,
        })
        return render_to_string('desktop/inclusion_tags/widgets/updates.html', context)
"""

# Shows

@register.tag
def dj_header(parser, token):
    return DJHeaderNode()

class DJHeaderNode(template.Node):
    def get_sections(self, request, castmember):
        sections = [
        {
            'slug': 'blog',
            'title': 'Blog',
            'url': reverse('shows_dj_blog', kwargs={'slug': castmember.slug}),
        },
        {
            'slug': 'profile',
            'title': 'Profile',
            'url': reverse('shows_dj_profile', kwargs={'slug': castmember.slug}),
        },
        #{
        #    'slug': 'contact',
        #    'title': 'Contact',
        #    'url': 'test',
        #},
        #{
        #    'slug': 'appearances',
        #    'title': 'Appearances',
        #    'url': 'test',
        #},
        ]

        current_section = request.path.split('/')[-2]
        if current_section not in [s['slug'] for s in sections]:
            current_section = 'blog'

        for s in sections:
            if current_section == s['slug']:
                current_section = s
                break

        return sections, current_section

    def render(self, context):
        request = context['request']
        castmember = context['castmember']
        sections, current_section = self.get_sections(request, castmember)
        
        owner = castmember.owner
        profile = owner.profile if owner else None

        shows = castmember.show_set.permitted()
        show_times = []
        for show in shows:
            show_times += show.show_times()
            if len(show_times) > 2:
                break
        show_times =show_times[:2]

        context.update({
            'profile': profile,
            'show_times': show_times,
            'sections': sections,
            'current_section': current_section,
        })
        return render_to_string('desktop/inclusion_tags/shows/dj_header.html', context)


@register.tag
def social_updates(parser, token):
    return SocialUpdatesNode()


class SocialUpdatesNode(template.Node):
    
    def render(self, context):
        castmember = context['castmember']
        
        owner = castmember.owner
        if owner:
            profile = owner.profile
        else:
            profile = None
        
        if profile:
            context.update({
                'updates': profile.tweets(),
            })
        
        return render_to_string('desktop/inclusion_tags/widgets/dj_social_updates.html', context)
