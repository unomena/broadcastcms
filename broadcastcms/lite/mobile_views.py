import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import Http404

from broadcastcms import public
from broadcastcms.show.models import Show, CastMember
from broadcastcms.base.models import ContentBase
from broadcastcms.calendar.models import Entry


# Shows
def shows_line_up(request, weekday=None):
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

def shows_dj_blog(request, dj_slug):
    context = RequestContext(request, {})
    obj = get_object_or_404(CastMember, slug=dj_slug)
    context.update({
        'is_castmember': True,
        'obj': obj,
    })
    
    return render_to_response('mobile/content/shows/dj.html', context)

# Accounts
def account_login(request):
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(
                username=username, 
                password=password
            )
            if user:
                auth.login(request, user)
                return HttpResponse("true")
            else:
                return HttpResponse("'Incorrect username or password.'")
    else:
        form = LoginForm()

    return render_to_response('mobile/accounts/sign-in.html', {'form': form})

def account_logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return account_links(request)
        
class CastMemberViews(object):
    def get_absolute_url(self):
        return "/show/%s/" % self.slug

class ContentBaseViews(object):
    def get_absolute_url(self):
        if self.owner:
            castmembers = CastMember.permitted.filter(owner=self.owner)
            if castmembers:
                return "/show/%s/%s/" % (castmembers[0].slug, self.slug)
        url_prefix = ''
        if self.classname == 'Gallery':
            url_prefix = 'gallery'
        elif self.classname == 'Competition':
            url_prefix = 'competition'
        elif self.classname == 'Event':
            url_prefix = 'event'
        elif self.classname == 'Post':
            url_prefix = 'news'
        else:
            return None
        return "/%s/%s/" % (url_prefix, self.slug)

public.site.register(CastMember, CastMemberViews)
public.site.register(ContentBase, ContentBaseViews)