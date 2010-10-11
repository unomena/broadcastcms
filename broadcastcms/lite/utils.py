import calendar
from datetime import date, datetime
import threading

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, mail_managers
    
from voting.models import Vote
            
from broadcastcms.label.models import Label

def paging(queryset, request_key, request, size=10):
    paginator = Paginator(queryset, size)
    page = request.GET.get(request_key, '1')
    try:
        page_number = int(page)
    except ValueError:
        if page == 'last':
            page_number = paginator.num_pages
        else:
            # Page is not 'last', nor can it be converted to an int.
            raise Http404
    try:
        page_obj = paginator.page(page_number)
    except (EmptyPage, InvalidPage):
        page_obj = paginator.page(1)
    
    page_obj.key = request_key
    return page_obj

def order_by_created(items):
    return items.order_by("-created")

def order_by_likes(items):
    items = [item.contentbase for item in items.all()]
    items.sort(reverse=True, key=lambda x: Vote.objects.get_score(x)['score'])
    items = [item.as_leaf_class() for item in items]
    return items

def filter_by_upcoming(items):
    return items.upcoming()

def filter_by_thisweekend(items):
    return items.thisweekend()

class Sorter(object):
    sorters = [
        {
            'slug': 'most-recent',
            'title': 'Most Recent',
            'sorter': order_by_created,
        },
        {
            'slug': 'most-liked',
            'title': 'Most Liked',
            'sorter': order_by_likes,
        },
    ]

    def __init__(self, list, view_name, request_key, request):
        self.object_list = list
        self.view_url = reverse(view_name)
        self.key = request_key
        self.sorter = None
        sorter_slug = str(request.REQUEST.get(request_key, ''))
       
        if self.object_list:
            if sorter_slug not in [s['slug'] for s in self.sorters]:
                self.sorter = self.sorters[0]
            else:
                for sorter in self.sorters:
                    if sorter_slug == sorter['slug']:
                        self.sorter = sorter
                        break

            self.object_list = self.sorter['sorter'](self.object_list)


class EventSorter(Sorter):
    sorters = [
        {
            'slug': 'upcoming',
            'title': 'Upcoming',
            'sorter': filter_by_upcoming,
        },
        {
            'slug': 'this-weekend',
            'title': 'This Weekend',
            'sorter': filter_by_thisweekend,
        },
    ]


class QuerysetModifier(object):
    def __init__(self, get_value):
        self.get_value = get_value


class EntryWeekQuerysetModifier(QuerysetModifier):
    def updateQuery(self, queryset):
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        today = date.today()

        if self.get_value in days:
            offset = days.index(self.get_value) - today.weekday()
        else:
            offset = 0

        return queryset.day(offset)


class ChartQuerysetModifier(QuerysetModifier):
    def __init__(self, get_value, page_length):
        self.page_length = page_length
        super(ChartQuerysetModifier, self).__init__(get_value)

    def updateQuery(self, queryset):
        return queryset[int(self.get_value): int(self.get_value) + self.page_length]


class MostLikedQuerysetModifier(QuerysetModifier):
    def updateQuery(self, queryset):
        queryset = queryset.extra(
            select={
                'score': 'SELECT COUNT(*) FROM votes WHERE votes.object_id = base_contentbase.modelbase_ptr_id AND votes.vote = 1'
            },
        )
        queryset = queryset.order_by('-score', '-created')
        return queryset


class MostRecentQuerysetModifier(QuerysetModifier):
    def updateQuery(self, queryset):
        return queryset.order_by("-created")

class LabeledQuerysetModifier(QuerysetModifier):
    def __init__(self, get_value, label):
        self.label = label
        super(LabeledQuerysetModifier, self).__init__(get_value)

    def updateQuery(self, queryset):
        return queryset.filter(labels=self.label)
        
        
# Queryset Modifiers for Multimedia page
class MediaQuerysetModifier(QuerysetModifier):
    def __init__(self, get_value):
        self.filter_classes = ['Video', 'Gallery']
        if get_value == 'videos':
            self.filter_classes = ['Video', ]
        elif get_value == 'galleries':
            self.filter_classes = ['Gallery', ]
            
        super(QuerysetModifier, self).__init__(get_value)
            
        
    def updateQuery(self, queryset):
        return queryset.filter(classname__in=self.filter_classes)


class MediaSubQuerysetModifier(QuerysetModifier):
    def updateQuery(self, queryset):
        if self.get_value == 'goodhope':
            return queryset.filter(owner__is_staff=True)
        elif self.get_value == 'globalcitizens':
            return queryset.filter(owner__is_staff=False)
        # unmodified
        return queryset


class PageMenu(object):
    request_key = None

    def __init__(self, request):
        self.request = request
        for item in self.items:
            if item.has_key('view_name'):
                if item.has_key('view_kwargs'):
                    item['path'] = reverse(item['view_name'], kwargs=item['view_kwargs'])
                else:
                    item['path'] = reverse(item['view_name'])
            item['url'] = ''
            if item.has_key('path'):
                item['url'] += item['path']
            if item.has_key('get_value'):
                item['url'] += "?%s=%s" % (self.request_key, item['get_value'])

    @property
    def get_value(self):
        get_value = str(self.request.REQUEST.get(self.request_key, None))
        if get_value:
            valid_get_values = []
            for item in self.items:
                if item.has_key('get_value'):
                    valid_get_values.append(item['get_value'])
            if get_value in valid_get_values:
                return get_value

        return None

    @property
    def active_item(self):
        get_value = self.get_value
        for item in self.items:
            active = False
            if item.has_key('get_value'):
                if get_value == item['get_value']:
                    active = True
                else:
                    active = False
                
            if item.has_key('path'):
                if self.request.path.startswith(item['path']):
                    active = True
                else:
                    active = False

            if active:
                return item

        for item in self.items:
            if item.has_key('default'):
                if item['default']:
                    return item

        return self.items[0]
                
    @property
    def title(self):
        active_item = self.active_item
        if active_item:
            return active_item['title']
        else:
            return None

    @property
    def queryset_modifier(self):
        active_item = self.active_item
        if active_item:
            return active_item['queryset_modifier'](active_item['get_value']) 
        else:
            return None
       
    def render(self):
        return render_to_string('desktop/menus/generic.html', {'object': self})


class ChartPageMenu(PageMenu):
    request_key = 'page'
    page_length = 10

    def __init__(self, request, chart):
        self.items = []
        self.chart = chart
        entry_count = chart.chartentries.permitted().count()
        slices = range(0, entry_count, self.page_length)
        for slice_start in slices:
            self.items.append({
                'title': '%s - %s' % (slice_start + 1, slice_start + self.page_length),
                'get_value': str(slice_start),
                'queryset_modifier': ChartQuerysetModifier,
            })
        super(ChartPageMenu, self).__init__(request)
    
    @property
    def queryset_modifier(self):
        active_item = self.active_item
        if active_item:
            return active_item['queryset_modifier'](active_item['get_value'], self.page_length)
        else:
            return None


class CompetitionsPageMenu(PageMenu):
    items = [
        {
            'title': 'Current Competitions',
            'view_name': 'competitions',
        },
        {
            'title': 'General Competition Rules',
            'view_name': 'competitions_rules',
        }
    ]


class CastMemberPageMenu(PageMenu):
    def __init__(self, request, castmember):
        self.items = [
            {
                'title': 'Blog',
                'view_name': 'shows_dj_blog',
                'view_kwargs': {'slug': castmember.slug},
            },
            {
                'title': 'Podcasts',
                'view_name': 'shows_dj_podcasts',
                'view_kwargs': {'slug': castmember.slug},
            },
            {
                'title': 'Profile',
                'view_name': 'shows_dj_profile',
                'view_kwargs': {'slug': castmember.slug},
            },
            {
                'title': 'Contact',
                'view_name': 'shows_dj_contact',
                'view_kwargs': {'slug': castmember.slug},
            },
            {
                'title': 'Appearances',
                'view_name': 'shows_dj_appearances',
                'view_kwargs': {'slug': castmember.slug},
            },
        ]
        super(CastMemberPageMenu, self).__init__(request)

    def render(self):
        return render_to_string('desktop/menus/generic.html', {'object': self})


class EntryWeekPageMenu(PageMenu):
    request_key = 'day'
    
    def __init__(self, request):
        self.items = [
            {
                'title': day[0],
                'get_value': day[1],
                'queryset_modifier': EntryWeekQuerysetModifier,
                'default': (str(calendar.day_name[datetime.now().weekday()]).lower() == day[1]),
            }
        for day in [('Mon', 'monday'), ('Tue', 'tuesday'), ('Wed', 'wednesday'), ('Thu', 'thursday'), ('Fri', 'friday'), ('Sat', 'saturday'), ('Sun', 'sunday'),]]
        super (EntryWeekPageMenu, self).__init__(request)

    
    @property
    def title(self):
        today = str(calendar.day_name[datetime.now().weekday()]).lower()
        active_item = self.active_item
        if active_item:
            if active_item['get_value'] == today:
                return 'Today'
            else:
                return active_item['get_value'].title


class OrderPageMenu(PageMenu):
    request_key = 'order-by'
    items = [
        {
            'title': 'Most Recent',
            'get_value': 'recent',
            'queryset_modifier': MostRecentQuerysetModifier,
        },
        {
            'title': 'Most Liked',
            'get_value': 'liked',
            'queryset_modifier': MostLikedQuerysetModifier,
        }
    ]


class ComplexPageMenu(PageMenu):
    def __init__(self, request):
        super(ComplexPageMenu, self).__init__(request)
        
        # get the currently active item
        active_item = self.active_item
        if active_item:
            # run through all possible sub-items
            for i in range(0, len(self.subitems)):
                self.subitems[i]['url'] = '%s&%s=%s' % (active_item['url'], self.subitems_request_key, self.subitems[i]['get_value'])
                
    
    @property
    def active_subitem(self):
        get_value = str(self.request.GET.get(self.subitems_request_key, ''))
        # if there is a sub-item specified
        if get_value:
            # search for the active sub-item
            for item in self.subitems:
                if get_value == item['get_value']:
                    return item
        
        # return the first available (default) sub-item
        return self.subitems[0]
    
    
    @property
    def subitem_queryset_modifier(self):
        active_subitem = self.active_subitem
        if active_subitem:
            return active_subitem['queryset_modifier'](active_subitem['get_value'])
        else:
            return None
        


class MultimediaPageMenu(ComplexPageMenu):
    request_key = 'media'
    items = [
        {
            'title'            : 'All Media',
            'get_value'        : 'all',
            'queryset_modifier': MediaQuerysetModifier,
        },
        {
            'title'            : 'Videos',
            'get_value'        : 'videos',
            'queryset_modifier': MediaQuerysetModifier,
        },
        {
            'title'            : 'Photo Galleries',
            'get_value'        : 'galleries',
            'queryset_modifier': MediaQuerysetModifier,
        },
    ]
    
    subitems_request_key = 'filter'
    subitems = [
        {
            'title'            : 'All',
            'get_value'        : 'all',
            'queryset_modifier': MediaSubQuerysetModifier,
        },
        {
            'title'            : 'Good Hope FM',
            'get_value'        : 'goodhope',
            'queryset_modifier': MediaSubQuerysetModifier,
        },
        {
            'title'            : 'Global Citizens',
            'get_value'        : 'globalcitizens',
            'queryset_modifier': MediaSubQuerysetModifier,
        },
    ]



class SubmitMultimediaPageMenu(PageMenu):
    verbose_title = 'I would like to submit the following:'
    
    items = [
        {
            'title': 'Pictures',
            'path' : '/multimedia/submit-photos/',
            'verbose_title': 'I would like to submit the following:',
        },
        {
            'title': 'Videos',
            'path' : '/multimedia/submit-video/',
            'verbose_title': 'I would like to submit the following:',
        }
    ]

    

class LabelPageMenu(PageMenu):
    request_key = 'label'
    
    def __init__(self, request, common_label):
        common_labeled_content = common_label.modelbase_set.permitted().select_related('labels')
        labels = set()
        for content in common_labeled_content:
            labels.update(content.labels.visible())

        labels = list(labels)
        labels.sort(reverse=False, key=lambda x: x.title)


        self.items = []
        for label in labels:
            self.items.append({
                'title': label.title,
                'get_value': label.title,
                'queryset_modifier': LabeledQuerysetModifier,
            })
        
        self.items = [{
                'title': 'All',
                'get_value': 'Reviews',
                'queryset_modifier': LabeledQuerysetModifier,
            }] + self.items
        
        super(LabelPageMenu, self).__init__(request)
    
    @property
    def queryset_modifier(self):
        active_item = self.active_item
        if active_item:
            filter_label = Label.objects.filter(title__exact=active_item['get_value'])
            return active_item['queryset_modifier'](active_item['get_value'], filter_label)
        else:
            return None
            

class Header(object):
    page_title_link = None
    
    @property
    def render_context(self):
        return {
            'page_title': self.page_title,
            'page_menu': self.page_menu,
            'page_title_link': reverse(self.page_title_link) if self.page_title_link else None,
        }
        
    def render(self):
        return render_to_string('desktop/headers/generic.html', self.render_context)


class CastMemberHeader(Header):
    page_title = 'Shows &amp; DJs'

    def __init__(self, request, castmember):
        self.castmember = castmember
        self.page_menu = CastMemberPageMenu(request, castmember)
    
    def render(self):
        # collect context variables
        context = self.render_context
        castmember = self.castmember
        owner = castmember.owner
        profile = owner.profile if owner else None
        
        # build show times
        shows = castmember.show_set.permitted()
        show_times = []
        for show in shows:
            show_times += show.show_times()
            if len(show_times) > 2:
                break
        show_times =show_times[:2]

        # update context
        context.update({
            'castmember': self.castmember,
            'profile': profile,
            'show_times': show_times,
        })

        return render_to_string('desktop/headers/castmember.html', context)


class ChartHeader(Header):
    def __init__(self, request, chart):
        self.page_title = chart.title
        self.page_menu = ChartPageMenu(request, chart)

    @property
    def render_context(self):
        context = super(ChartHeader, self).render_context
        context.update({
            'header_includes': ['desktop/includes/charts/header.html',]
        })
        return context


class CompetitionsHeader(Header):
    page_title = 'Win' 
    
    def __init__(self, request): 
        self.page_menu = CompetitionsPageMenu(request)


class CompetitionHeader(CompetitionsHeader):
    def __init__(self):
        self.page_menu = None


class GalleriesHeader(Header):
    page_title = 'Multimedia'
    page_title_link = 'galleries'
    
    def __init__(self, request):
        self.page_menu = MultimediaPageMenu(request)


class GalleryHeader(GalleriesHeader):
    page_title_link = 'galleries'
    
    def __init__(self):
        self.page_menu = None
        
        
class SubmitMultimediaHeader(Header):
    page_title = 'Send us your Pictures &amp; Videos'
    
    def __init__(self, request):
        self.page_menu = SubmitMultimediaPageMenu(request)
        
    
class MultimediaThanksHeader(Header):
    page_title = 'Thank You'
    
    def __init__(self):
        self.page_menu = None


class NewsHeader(Header):
    page_title = 'News'
    
    def __init__(self, request):
        self.page_menu = OrderPageMenu(request)


class NewsArticleHeader(NewsHeader):
    def __init__(self):
        self.page_menu = None

class ReviewsArticleHeader(Header):
    page_title = 'Reviews'

class ReviewsHeader(Header):
    page_title = 'Reviews'
    
    def __init__(self, request, common_label):
        self.page_menu = LabelPageMenu(request, common_label=common_label)

class ShowsHeader(Header):
    page_title = 'Shows &amp; DJs'
    
    def __init__(self, request):
        self.page_menu = EntryWeekPageMenu(request)


#------------------------------------------------------------------------------
def threaded_mail(subject, message, from_address, recipients):
    """
    Starts a separate thread to send an e-mail.
    """
    
    mail = EmailMessage(subject, message, from_address, recipients, headers={'From': from_address, 'Reply-To': from_address})
    t = threading.Thread(target=mail.send, kwargs={'fail_silently': False})
    t.setDaemon(True)
    t.start()


#------------------------------------------------------------------------------
def non_threaded_mail(subject, message, from_address, recipients):
    """
    Sends a mail in the current thread.
    """
    
    mail = EmailMessage(subject, message, from_address, recipients, headers={'From': from_address, 'Reply-To': from_address})
    mail.send(fail_silently=False)
    
