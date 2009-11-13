from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import redirect_to_login
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils import simplejson

import utils

from broadcastcms import public
from broadcastcms.base.models import ContentBase
from broadcastcms.calendar.models import Entry
from broadcastcms.competition.models import Competition
from broadcastcms.event.models import Event
from broadcastcms.gallery.models import Gallery
from broadcastcms.show.models import Show, CastMember
from broadcastcms.post.models import Post

from voting.models import Vote
from voting.views import *


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
    
# Generic
def custom_object_detail(request, slug, template, classname):
    context = RequestContext(request, {})
    obj = get_object_or_404(eval(classname), slug=slug)
    context.update({
        'obj': obj,
    })
    
    return render_to_response(template, context)

# Shows
def shows_line_up(request, weekday=None):
    context = RequestContext(request, {})
    
    weekdays = ['monday', 'tuesday', 'wednesday' , 'thursday', 'friday', 'saturday', 'sunday']
    day_offset = date.today().weekday()
    if weekday:
        if not weekday in weekdays:
            raise Http404
        day_offset = weekdays.index(weekday)
        is_today = False
    else:
        weekday = weekdays[day_offset]
        
    is_today = day_offset == date.today().weekday()
        
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

def account_logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return account_links(request)
    
def contact(request, dj_slug=None):
    context = RequestContext(request, {})
    form = ContactForm()
    sent = False

    if request.POST:
        form = form(request.POST)

        if form.is_valid(request):
            form.send_message()
            sent = True
    else:
        data = {}
        for key, item in form_class().fields.items():
            data.update({key: item.label})
        form = form_class(initial=data)
    
    context.update({
        'form': form,
        'sent': sent,
    })
    return render_to_response('mobile/content/contact.html', context)

# Vote without JS    
def httprequest_vote_on_object(request, model, direction,
    object_id=None, slug=None, slug_field=None):
    """
    Adapted from django-voting - vote.views.xmlhttprequest_vote_on_object
    Generic object vote function for use via HttpRequest.
    """
    VOTE_DIRECTIONS = (('up', 1), ('down', -1), ('clear', 0))
    
    if not request.user.is_authenticated():
        return HttpResponse('Not authenticated.')
    
    try:
        vote = dict(VOTE_DIRECTIONS)[direction]
    except KeyError:
        return HttpResponse('\'%s\' is not a valid vote type.' % direction)

    # Look up the object to be voted on
    lookup_kwargs = {}
    if object_id:
        lookup_kwargs['%s__exact' % model._meta.pk.name] = object_id
    elif slug and slug_field:
        lookup_kwargs['%s__exact' % slug_field] = slug
    else:
        return HttpResponse('Generic XMLHttpRequest vote view must be '
                            'called with either object_id or slug and '
                            'slug_field.')
    try:
        obj = model._default_manager.get(**lookup_kwargs)
    except ObjectDoesNotExist:
        return HttpResponse(
            'No %s found for %s.' % (model._meta.verbose_name, lookup_kwargs))

    # Vote and respond
    Vote.objects.record_vote(obj, request.user, vote)
    return HttpResponse(simplejson.dumps({
        'success': True,
        'score': Vote.objects.get_score(obj),
    }))
    
class CastMemberViews(object):
    def get_absolute_url(self):
        return "/show/%s/" % self.slug
    
class PostViews(object):
    def get_absolute_url(self):
        return "/news/%s/" % self.slug

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
public.site.register(Post, PostViews)
public.site.register(ContentBase, ContentBaseViews)