from datetime import datetime

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from broadcastcms.calendar.models import Entry
from broadcastcms.show.models import Credit, Show
from broadcastcms.base.models import ContentBase, ModelBase
from broadcastcms.radio.models import Song
from broadcastcms.cache.decorators import cache_view_function

register = template.Library()

# Skeleton

@register.tag
def account_links(parser, token):
    return AccountLinksNode()

class AccountLinksNode(template.Node):
    def render(self, context):
        """
        Renders anonymous avatar, sign in and sign up for anonymous users.
        Renders avatar, profile and sign out for authenticated users.
        """
        request = context['request']

        # get user and profile objects
        user = getattr(request, 'user', None)
        profile = None
        if user:
            if not user.is_anonymous():
                profile = user.profile

        context.update({
            'user': user,
            'profile': profile,
        })
        return render_to_string('desktop/inclusion_tags/skeleton/account_links.html', context)

@register.tag
def masthead(parser, token):
    return MastheadNode()

class MastheadNode(template.Node):
    @cache_view_function(10*60, respect_path=True, respect_user=True)
    def render(self, context):
        """
        Renders the sitewide masthead, including site logo, site section links, search and account links.
        Site section links are highlighted when on appropriate section.
        """
        section = context['section']
        items = [
            {'title': 'Shows &amp; DJs', 'url': reverse('shows_line_up'), 'current': section == 'shows'},
            {'title': 'Chart', 'url': reverse('chart'), 'current': section == 'chart'},
            {'title': 'Win', 'url': reverse('competitions'), 'current': section == 'competitions'},
            {'title': 'News', 'url': reverse('news'), 'current': section == 'news'},
            {'title': 'Events', 'url': reverse('events'), 'current': section == 'events'},
            {'title': 'Galleries', 'url': reverse('galleries'), 'current': section == 'galleries'},
        ]
        
        context.update({
            'items': items
        })

        return render_to_string('desktop/inclusion_tags/skeleton/masthead.html', context)

@register.tag
def mastfoot(parser, token):
    return MastfootNode()

class MastfootNode(template.Node):
    @cache_view_function(10*60)
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
def metrics(parser, token):
    return MetricsNode()

class MetricsNode(template.Node):
    @cache_view_function(10*60)
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
def features(parser, token):
    return FeaturesNode()

class FeaturesNode(template.Node):
    @cache_view_function(10*60)
    def render(self, context):
        """
        Renders the homepage features box. Content is featured by labeling it
        and then selecting labels to feature in the setting object's homepage featured labels field.
        Only public content and visible labels will render.
        A maximum of 3 labels will render.
        """
        # grab featured labels from settings
        settings = context['settings']
        homepage_featured_labels = settings.homepage_featured_labels.filter(is_visible=True)[:3]
       
        # build a dictionary with label, content and url keys corresponding to 
        # a featured label and its last created content.
        features = []
        for label in homepage_featured_labels:
            content = ModelBase.objects.permitted().filter(labels__exact=label).order_by('-pk')
            if content: 
                content = content[0].as_leaf_class()
                # for objects with a url field return the fields value as its url
                # otherwise try and generate a url from the object's url method
                try:
                    url = content.url(context)
                except TypeError:
                    url = content.url
                feature = {
                    'label': label, 
                    'content': content,
                    'url': url,
                }
                features.append(feature)
    
        context.update({
            'features': features
        })
        return render_to_string('desktop/inclusion_tags/home/features.html', context)

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

    def get_primary_castmember(self, show):
        """
        Returns the primary public castmember for the given show.
        Primary castmember is determined by credit roles.
        """
        credits = show.credits.all().filter(castmember__is_public=True).order_by('role')
        return credits[0].castmember if credits else None
    
    @cache_view_function(2*60)
    def render(self, context):
        """
        Renders the homepage On Air box containing details on the
        current show and current song as well as listen live, studio
        cam and castmember blog links
        """
        # get a show to display, either currently on air or coming up
        on_air = True
        show_entry = self.get_public_on_air_entry(Show)
        if not show_entry:
            show_entry = self.get_public_next_on_air_entry(Show)
            on_air = False
        show = show_entry.content.as_leaf_class() if show_entry else None
       
        # get the primary castmember for the current on air show
        primary_castmember = self.get_primary_castmember(show) if show else None
        
        # get the current playing song and artist info
        song_entry = self.get_public_on_air_entry(Song)
        song = song_entry.content.as_leaf_class() if song_entry else None
        artist = song.credits.all().filter(artist__is_public=True).order_by('role') if song else None

        context.update({
            'entry': show_entry,
            'show': show,
            'on_air': on_air,
            'primary_castmember': primary_castmember,
            'song': song,
            'artist': artist,
        })
        return render_to_string('desktop/inclusion_tags/home/on_air.html', context)

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
def account_menu(parser, token):
    return AccountMenuNode()

class AccountMenuNode(template.Node):
    def render(self, context):
        request = context['request']

        menu_items = [{
                'title': 'Profile',
                'section': 'profile',
                'url': reverse('account_profile'),
            },
            {
                'title': 'Picture',
                'section': 'picture',
                'url': reverse('account_picture'),
            },
            {
                'title': 'Subscriptions',
                'section': 'subscriptions',
                'url': reverse('account_subscriptions'),
            },
        ]
        account_section = request.path.split('/')[-2]
       
        profile = request.user.profile

        context.update({
            'menu_items': menu_items,
            'account_section': account_section,
            'profile': profile,
        })
        return render_to_string('desktop/inclusion_tags/account/menu.html', context)

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
        primary_castmember = self.get_primary_castmember(show) if show else None
        
        # get the current playing song and artist info
        song_entry = self.get_public_on_air_entry(Song)
        song = song_entry.content.as_leaf_class() if song_entry else None
        artist = song.get_primary_artist() if song else None
        
        next_entry = self.get_next_entry(Show)
        next_show = next_entry.content.as_leaf_class() if next_entry else None
        next_castmember = self.get_primary_castmember(next_show) if next_show else None
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
