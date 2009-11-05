import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template.defaultfilters import date as datefilter

from broadcastcms import public
from broadcastcms.show.models import Show, CastMember
from broadcastcms.base.models import ContentBase
from broadcastcms.calendar.models import Entry



def shows(request, weekday=None):
    context = RequestContext(request, {})
    
    weekdays = ['monday', 'tuesday', 'wednesday' , 'thursday', 'friday', 'saturday', 'sunday']
    
    day_offset = datetime.date.today().weekday()
    if weekday:
        day_offset = weekdays.index(weekday)
        
    queryset = Entry.objects.permitted().day(day_offset).by_content_type(Show).order_by('start')
    context.update({
        'obj_list': queryset,
    })
    
    return render_to_response('mobile/content/shows/shows.html', context)


def search_results(request):
    context = RequestContext(request, {})
    
def shows_line_up(request, template_name='desktop/generic/object_listing_block.html'):
    queryset=Entry.objects.permitted().by_content_type(Show).order_by('start') 
    page_menu=utils.EntryWeekPageMenu(request)
    queryset_modifiers = [page_menu.queryset_modifier,]
    for queryset_modifier in queryset_modifiers:
        queryset = queryset_modifier.updateQuery(queryset)

    return list_detail.object_list(
        request=request,
        queryset=queryset,
        template_name=template_name,
        extra_context={
            'page_title': 'Shows &amp; DJs',
            'page_menu': page_menu,
        },
    )

class CastMemberViews(object):
    def get_absolute_url(self):
        return reverse('shows_dj_blog', kwargs={'slug': self.slug})

class ContentBaseViews(object):
    def get_absolute_url(self):
        if self.owner:
            castmembers = CastMember.permitted.filter(owner=self.owner)
            if castmembers:
                return "/shows/%s/%s/" % (castmembers[0].slug, self.slug)
        url_prefix = ''
        if self.classname == 'Gallery':
            url_prefix = 'galleries'
        elif self.classname == 'Competition':
            url_prefix = 'competitions'
        elif self.classname == 'Event':
            url_prefix = 'events'
        elif self.classname == 'Post':
            url_prefix = 'news'
        else:
            return None
        return "/%s/%s/" % (url_prefix, self.slug)

public.site.register(CastMember, CastMemberViews)
public.site.register(ContentBase, ContentBaseViews)
