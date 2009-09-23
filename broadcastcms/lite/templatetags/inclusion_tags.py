from datetime import datetime

from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from broadcastcms.calendar.models import Entry
from broadcastcms.show.models import Show
from broadcastcms.base.models import ContentBase, ModelBase
from broadcastcms.radio.models import Song

register = template.Library()

# Skeleton

@register.tag
def account_links(parser, token):
    return AccountLinksNode()

class AccountLinksNode(template.Node):
    def render(self, context):
        request = context['request']
        user = request.user
        profile = None
        if user:
            if not user.is_anonymous():
                profile = request.user.profile

        context.update({
            'user': user,
            'profile': profile,
        })
        return render_to_string('inclusion_tags/skeleton/account_links.html', context)

@register.tag
def masthead(parser, token):
    return MastheadNode()

class MastheadNode(template.Node):
    def render(self, context):
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

        return render_to_string('inclusion_tags/skeleton/masthead.html', context)

@register.tag
def mastfoot(parser, token):
    return MastfootNode()

class MastfootNode(template.Node):
    def render(self, context):
        return render_to_string('inclusion_tags/skeleton/mastfoot.html', context)


# Home

@register.tag
def home_advert(parser, token):
    return HomeAdvertNode()

class HomeAdvertNode(template.Node):
    def render(self, context):
        section = context['section']
        settings = context['settings']
        banners = settings.get_section_banners(section)
        return banners[0].render() if banners else ""

@register.tag
def features(parser, token):
    return FeaturesNode()

class FeaturesNode(template.Node):
    def render(self, context):
        features = []
        settings = context['settings']
        homepage_featured_labels = settings.homepage_featured_labels.all()
        
        for label in homepage_featured_labels:
            content = ContentBase.objects.permitted().filter(labels__exact=label)
            if content: features.append({'label': label, 'content': content[0]})

        context.update({
            'features': features
        })
        return render_to_string('inclusion_tags/home/features.html', context)

@register.tag
def on_air(parser, token):
    return OnAirNode()

class OnAirNode(template.Node):
    def get_on_air_entry(self, content_type):
        valid_entry = None
        now = datetime.now()
        
        entries = Entry.objects.permitted().by_content_type(content_type).filter(start__lt=now, end__gt=now).order_by('start')
        for entry in entries:
            if entry.content.is_public:
                valid_entry = entry
                break

        return valid_entry

    def get_primary_castmember(self, show):
        castmember = None
        credits = show.credits.all().order_by('role')
        for credit in credits:
            castmember = credit.castmember
            if castmember.is_public:
                break

        return castmember
    
    def get_primary_artist(self, song):
        artist = None
        credits = song.credits.all().order_by('role')
        for credit in credits:
            artist = credit.artist
            if artist.is_public:
                break

        return artist
        
    def render(self, context):
        show_entry = self.get_on_air_entry(Show)
        show = show_entry.content.as_leaf_class() if show_entry else None
        if not show:
            return ''
        castmember = self.get_primary_castmember(show) if show else None
        
        song_entry = self.get_on_air_entry(Song)
        song = song_entry.content.as_leaf_class() if song_entry else None
        artist = self.get_primary_artist(song) if song else None

        context = {
            'entry': show_entry,
            'show': show,
            'castmember': castmember,
            'song': song,
            'artist': artist,
        }
        return render_to_string('inclusion_tags/home/on_air.html', context)

        return ''

@register.tag
def home_updates(parser, token):
    return HomeUpdatesNode()

class HomeUpdatesNode(template.Node):
    tray_length = 3
    panel_rows = 2
    count = 18

    def get_instances(self, context):
        settings = context['settings']
        update_types = [update_type.model_class().__name__ for update_type in settings.update_types.all()]
        return ContentBase.permitted.filter(classname__in=update_types).order_by("-created")
  
    def build_panels(self, instances):
        trays = []
        slices = range(0, len(instances), self.tray_length)
        for slice_start in slices:
            trays.append(instances[slice_start: slice_start + self.tray_length])

        panels = []
        slices = range(0, len(trays), self.panel_rows)
        for slice_start in slices:
            panels.append(trays[slice_start: slice_start + self.panel_rows])

        return panels

    def render(self, context):
        instances = [instance.as_leaf_class() for instance in self.get_instances(context)[:self.count]]
        panels = self.build_panels(instances)
       
        context.update({
            'panels': panels,
        })
        return render_to_string('inclusion_tags/misc/updates.html', context)

# Popup

@register.tag
def popup_updates(parser, token):
    return PopupUpdatesNode()

class PopupUpdatesNode(HomeUpdatesNode):
    tray_length = 1
    panel_rows = 3
    count = 9

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
            return render_to_string('inclusion_tags/misc/paging.html', context)
        return ''

@register.tag
def post_head(parser, token):
    token = token.split_contents()
    if not len(token) == 2:
        raise template.TemplateSytaxError, '%r tag requires exactly 1 argument.' % token[0]
    return PostHeadNode(token[1])

class PostHeadNode(template.Node):
    def __init__(self, instance):
        self.instance = template.Variable(instance)

    def render(self, context):
        instance = self.instance.resolve(context)
        host = "http://%s" % context['request'].META['HTTP_HOST']
        vote_url = reverse('xmlhttprequest_vote_on_object', kwargs={'slug': instance.slug})
        context.update({
            'instance': instance,
            'owner': instance.owner,
            'host': host,
            'vote_url': vote_url,
        })
        return render_to_string('inclusion_tags/misc/post_head.html', context)

@register.tag
def comments(parser, token):
    return CommentsNode()

class CommentsNode(template.Node):
    def render(self, context):
        context = {}
        return render_to_string('inclusion_tags/misc/comments.html', context)

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
        return render_to_string('inclusion_tags/misc/sorting.html', context)

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
        return render_to_string('inclusion_tags/account/menu.html', context)


# Widgets

@register.tag
def advert(parser, token):
    return AdvertNode()

class AdvertNode(template.Node):
    def render(self, context):
        section = context['section']
        settings = context['settings']
        banners = settings.get_section_banners(section)
        context = {
            'banners': banners,
        }
        return render_to_string('inclusion_tags/widgets/advert.html', context)


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

    def render(self, context):
        show_entry = self.get_on_air_entry(Show)
        show = show_entry.content.as_leaf_class() if show_entry else None
        castmember = self.get_primary_castmember(show) if show else None
        
        song_entry = self.get_on_air_entry(Song)
        song = song_entry.content.as_leaf_class() if song_entry else None
        artist = self.get_primary_artist(song) if song else None
        
        next_entry = self.get_next_entry(Show)
        next_show = next_entry.content.as_leaf_class() if next_entry else None
        next_castmember = self.get_primary_castmember(next_show) if next_show else None

        context = {
            'entry': show_entry,
            'show': show,
            'castmember': castmember,
            'song': song,
            'artist': artist,
            'next_show': next_show,
            'next_castmember': next_castmember,
        }
        return render_to_string('inclusion_tags/widgets/now_playing.html', context)

@register.tag
def updates(parser, token):
    return UpdatesNode()

class UpdatesNode(HomeUpdatesNode):
        
    def render(self, context):
        instances = [instance.as_leaf_class() for instance in self.get_instances(context)[:5]]
        context.update({
            'instances': instances,
        })
        return render_to_string('inclusion_tags/widgets/updates.html', context)

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
        {
            'slug': 'contact',
            'title': 'Contact',
            'url': 'test',
        },
        {
            'slug': 'appearances',
            'title': 'Appearances',
            'url': 'test',
        },
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
        return render_to_string('inclusion_tags/shows/dj_header.html', context)
