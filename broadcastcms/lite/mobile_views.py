import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template.defaultfilters import date as datefilter
from django.http import Http404

from broadcastcms import public
from broadcastcms.show.models import Show, CastMember
from broadcastcms.base.models import ContentBase
from broadcastcms.calendar.models import Entry


def shows(request, weekday=None):
    context = RequestContext(request, {})
    
    weekdays = ['monday', 'tuesday', 'wednesday' , 'thursday', 'friday', 'saturday', 'sunday']
    day_offset = datetime.date.today().weekday()
    if weekday:
        if not weekday in weekdays:
            raise Http404
        day_offset = weekdays.index(weekday)
        is_today = False
    else:
        weekday = weekdays[day_offset]
        
    is_today = day_offset == datetime.date.today().weekday()
        
    obj_list = Entry.objects.permitted().day(day_offset).by_content_type(Show).order_by('start')
    context.update({
        'weekdays': weekdays,
        'weekday': weekday,
        'is_today': is_today,
        'obj_list': obj_list,
    })
    
    return render_to_response('mobile/content/shows/shows.html', context)


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
