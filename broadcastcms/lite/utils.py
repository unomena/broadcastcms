from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse

def paging(list, request_key, request, size=10):
    paginator = Paginator(list, size)
    page = int(request.REQUEST.get(request_key, '1'))
    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page = paginator.page(1)
    page.key = request_key
    return page

def order_by_created(items):
    return items.order_by("-created")

def order_by_likes(items):
    raise NotImplementedError

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
