from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.contrib.auth.models import User
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
from broadcastcms.lite.forms import MobileLoginForm, MobileRegistrationForm, MobileProfileForm
from broadcastcms.gallery.models import Gallery
from broadcastcms.show.models import Show, CastMember
from broadcastcms.post.models import Post

from voting.models import Vote
from voting.views import *


# Accounts
def account_login(request):
    form = MobileLoginForm()
    error = ''
    if request.POST:
        form = MobileLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(
                username=username, 
                password=password
            )
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(request.session.get('return_path', '/'))
            else:
                error = 'Either your username or password is incorrect. Please try again'
    else:
        request.session['return_path'] = request.META['HTTP_REFERER']
            
    return render_to_response('mobile/content/accounts/sign-in.html', {'form': form, 'errors': error})

def account_logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect('/')

def account_subscriptions(request):
    if not request.user.is_authenticated():
       raise Http404
    
    context = RequestContext(request, {})
    user = request.user
    profile = request.user.profile
        
    if request.POST:
        form = ProfileSubscriptionsForm(request.POST)
        if form.is_valid():
            profile.email_subscribe = form.cleaned_data['email_subscribe']
            profile.sms_subscribe = form.cleaned_data['sms_subscribe']
            profile.save()
    else:
        data = {
            'email_subscribe': profile.email_subscribe,
            'sms_subscribe': profile.sms_subscribe,
        }
        form = ProfileSubscriptionsForm(initial=data)

    context.update({
        'form': form,
    })
    return render_to_response('mobile/content/account/sign-up.html', context)
    
def account_register(request):
    
    form = MobileRegistrationForm()
    if request.POST:
        form = MobileRegistrationForm(request.POST)

        if form.is_valid():
            
            # Get cleaned form values
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            mobile_number = form.cleaned_data['mobile_number']
            email_address = form.cleaned_data['email_address']
            email_subscribe = form.cleaned_data['email_subscribe']
            sms_subscribe = form.cleaned_data['sms_subscribe']

            # Create user
            user = User.objects.create_user(
                username = username,
                password = password,
                email = email_address
            )
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Create profile
            profile = user.profile
            profile.mobile_number = mobile_number
            profile.email_subscribe = email_subscribe
            profile.sms_subscribe = sms_subscribe
            profile.save()
            '''
            # Send confirmation mail
            message, subject = mailer_new_user(request, username, password)
            mail_user(subject, message, user, content_subtype="html", fail_silently=False)
            '''
            # Authenticate and login user
            user = auth.authenticate(
                username=username, 
                password=password
            )
            if user:
                auth.login(request, user)
            
            return HttpResponseRedirect('/account/sign-up/success/')
    
    context = RequestContext(request, {})
    context.update({
        'form': form,
    })
    return render_to_response('mobile/content/accounts/sign-up.html', context)
    
def account_confirm(request, result):
    if result == 'success': result = True
    else: result = False
    context = RequestContext(request, {})
    context.update({
        'result': result,
    })
    return render_to_response('mobile/content/accounts/sign-up-result.html', context)
    
def account_profile(request):
    """
    TODO: This view seems very flimsy, refactor.
    """
    if not request.user.is_authenticated():
       raise Http404
    
    context = RequestContext(request, {})
    user = request.user
    profile = request.user.profile
        
    if request.POST:
        form = MobileProfileForm(request.POST)

        # If no password supplied remove the password fields thereby ignoring them and not changing the password
        password = form.fields['password'].widget.value_from_datadict(form.data, form.files, form.add_prefix('password'))
        password_confirm = form.fields['password_confirm'].widget.value_from_datadict(form.data, form.files, form.add_prefix('password_confirm'))
        if not password:
            password_field = form.fields['password']
            del form.fields['password']
            password_confirm_field = form.fields['password_confirm']
            del form.fields['password_confirm']
        
        # Prevent user's own username triggering an error
        username = form.fields['username'].widget.value_from_datadict(form.data, form.files, form.add_prefix('username'))
        if user.username == username:
            username_field = form.fields['username']
            del form.fields['username']

        if form.is_valid():
            # Readd fields removed for validation
            if user.username == username:
                form.fields['username'] = username_field
                form.cleaned_data['username'] = username
            
            if not password:
                form.fields['password'] = password_field
                form.cleaned_data['password'] = password
                form.fields['password_confirm'] = password_confirm_field
                form.cleaned_data['password_confirm'] = password_confirm
            
            # Get cleaned form values
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email_address = form.cleaned_data['email_address']
            mobile_number = form.cleaned_data['mobile_number']

            # Update user
            user.username = username
            user.email = email_address
            user.first_name = first_name
            user.last_name = last_name
            if password:
                user.set_password(password)
            user.save()

            # Update profile
            profile.mobile_number = mobile_number
            profile.save()
        else:
            # Readd fields removed for validation
            if user.username == username:
                form.fields['username'] = username_field
            
            if not password:
                form.fields['password'] = password_field
                form.fields['password_confirm'] = password_confirm_field
    else:
        province = profile.province
        if province: province = province.id
            
        data = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email_address': user.email,
            'mobile_number': profile.mobile_number,
            'password': '',
        }
            
        form = MobileProfileForm(initial=data)

    context.update({
        'form': form,
    })
    return render_to_response('mobile/content/accounts/profile.html', context)
    
def httprequest_vote_on_object(request, model, direction,
    object_id=None, slug=None, slug_field=None):
    """
    Adapted from django-voting - vote.views.xmlhttprequest_vote_on_object
    Generic object vote function for use via HttpRequest.
    """
    VOTE_DIRECTIONS = (('up', 1), ('down', -1), ('clear', 0))
    
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/account/sign-in/')
    
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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

   
# Generic
def custom_object_detail(request, slug, dj_slug=None, classname=None, comment_add=False):
    context = RequestContext(request, {})
    template_dict = {
        'Competition': 'mobile/content/competitions/competition-details.html',
        'Event': 'mobile/content/events/event-details.html',
        'Gallery': 'mobile/content/galleries/gallery-details.html',
        'Post': 'mobile/content/news/news-article.html',
    }
    
    if classname:
        obj = get_object_or_404(eval(classname), slug=slug)
    else:
        obj = ContentBase.objects.permitted().filter(slug=slug)
        obj = obj[0].as_leaf_class() if obj else None
        classname = obj.classname
        
    if not obj: raise Http404
        
    if classname == 'Event':
        obj = obj.entries.all()[0]
    context.update({
        'obj': obj,
        'comment_add': comment_add,
    })
    
    return render_to_response(template_dict[classname], context)


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