from datetime import date, datetime, timedelta
import calendar
import mimetypes

from django import template
from django.conf import settings
from django.contrib import auth
from django.contrib import comments
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.comments import signals
from django.contrib.comments.models import Comment
from django.contrib.comments.views.comments import CommentPostBadRequest
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.forms.util import ValidationError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson, feedgenerator
from django.utils.http import urlencode
from django.views.generic import list_detail

from friends.models import FriendshipInvitation, Friendship
from user_messages.models import Message
from voting.models import Vote

from broadcastcms import public
from broadcastcms.activity.models import ActivityEvent
from broadcastcms.banner.models import CodeBanner, ImageBanner
from broadcastcms.base.models import ContentBase
from broadcastcms.calendar.models import Entry
from broadcastcms.cache.decorators import cache_for_nginx
from broadcastcms.chart.models import Chart, ChartEntry
from broadcastcms.competition.models import Competition
from broadcastcms.event.models import Event, Appearance
from broadcastcms.gallery.models import Gallery
from broadcastcms.integration.captchas import ReCaptcha
from broadcastcms.label.models import Label
from broadcastcms.lite.context_processors import determine_section
from broadcastcms.podcast.models import PodcastStandalone
from broadcastcms.post.models import Post
from broadcastcms.radio.models import Song
from broadcastcms.richtext.fields import RichTextField
from broadcastcms.scaledimage.fields import get_image_scales
from broadcastcms.show.models import Show, CastMember, Credit
from broadcastcms.status.models import StatusUpdate
from broadcastcms.utils import mail_user
from broadcastcms.utils.decorators import ajax_required

from forms import make_competition_form, make_contact_form, LoginForm, ProfileForm, ProfilePictureForm, ProfileSubscriptionsForm, RegistrationForm, _BaseCastmemberContactForm
from templatetags.desktop_inclusion_tags import AccountLinksNode, CommentsNode, StatusUpdateNode, HomeFriendsNode, HomeStatusUpdatesNode, LikesStampNode
import utils

def facebook_login_redirect(request, redirect_url=None):
    """
    Determines whether or not to redirect to account setup view
    after facebook login. Returns json fo the form 
    {'new_user': True/False, 'redirect': 'some/url/'}
    """
    # User is logging in
    url = reverse('facebook_setup')
    if request.POST.get(REDIRECT_FIELD_NAME,False):
        url += "?%s=%s" % (REDIRECT_FIELD_NAME, request.POST[REDIRECT_FIELD_NAME])
    elif redirect_url:
        url += "?%s=%s" % (REDIRECT_FIELD_NAME, redirect_url)
    user = authenticate(request=request)
    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
            return HttpResponse(simplejson.dumps({"new_user": False, "redirect": url}))
        else:
            raise FacebookAuthError('This account is disabled.')
    elif request.facebook.uid:
        #we have to set this user up
        return HttpResponse(simplejson.dumps({"new_user": True, "redirect": url}))

def resolve_pattern(request):
    from django.core import urlresolvers
    from django.core.urlresolvers import Resolver404
    from django.conf import settings
    urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
    self = urlresolvers.RegexURLResolver(r'^/', urlconf)
    path = request.path_info
    
    tried = []
    match = self.regex.search(path)
    if match:
        new_path = path[match.end():]
        for pattern in self.url_patterns:
            try:
                sub_match = pattern.resolve(new_path)
            except Resolver404, e:
                sub_tried = e.args[0].get('tried')
                if sub_tried is not None:
                    tried.extend([(pattern.regex.pattern + '   ' + t) for t in sub_tried])
                else:
                    tried.append(pattern.regex.pattern)
            else:
                if sub_match:
                    sub_match_dict = dict([(smart_str(k), v) for k, v in match.groupdict().items()])
                    sub_match_dict.update(self.default_kwargs)
                    for k, v in sub_match[2].iteritems():
                        sub_match_dict[smart_str(k)] = v
                    return pattern
                tried.append(pattern.regex.pattern)
        raise Resolver404, {'tried': tried, 'path': new_path}
    raise Resolver404, {'path' : path}

@cache_for_nginx(60*1)
def layout_view(request):
    from broadcastcms.widgets.models import Layout
    pattern = resolve_pattern(request)
    layout = get_object_or_404(Layout, view_name=pattern.name, is_public=True)
    return layout.as_leaf_class().render(request)

def obj_render_wrapper(request, obj, context=None):
    """
    Thin wrapper exposing an objects's render method as a view.
    """
    if not context:
        context = RequestContext(request, {})
    return HttpResponse(obj.render(context))

def obj_render_content_wrapper(request, obj, context=None):
    """
    Thin wrapper exposing an objects's render_content method as a view.
    """
    if not context:
        context = RequestContext(request, {})
    return HttpResponse(obj.render_content(context))

@cache_for_nginx(60*1)
def ssi_account_links_node(request):
    """
    Returns the account_links tag's content as a response.
    """
    return obj_render_content_wrapper(request, AccountLinksNode())

@cache_for_nginx(60*1)
def ssi_status_update_node(request):
    """
    Returns the status_update tag's content as a response.
    """
    return obj_render_content_wrapper(request, StatusUpdateNode())

@cache_for_nginx(60*1)
def ssi_widget(request, slug):
    """
    Returns a widgets render_content response.
    """
    from broadcastcms.widgets.models import Widget
    widget = get_object_or_404(Widget, slug=slug).get_leaf()
    return obj_render_content_wrapper(request, widget)

@cache_for_nginx(60*10)
def session_your_friends(request):
    """
    Exposes the YourFriends widget as a view.
    """
    return obj_render_content_wrapper(request, YourFriends())

@cache_for_nginx(60*1)
def session_status_updates(request):
    """
    Exposes the StatusUpdates widget as a view.
    """
    return obj_render_content_wrapper(request, StatusUpdates())
    
@ajax_required
def ajax_likes_stamp(request, slug):
    """
    Exposes the LikesStampNode inclusion tag as a view.
    """
    context = RequestContext(request, {})
    instance = get_object_or_404(ContentBase, slug=slug)

    context.update({
        'instance': instance 
    })
    obj = template.Variable('instance')

    return obj_render_wrapper(request, LikesStampNode(obj), context)

@ajax_required
def ajax_sign_out(request):
    if request.user.is_authenticated():
        auth.logout(request)
    
    return HttpResponse("")
   
# RSS
def rss_object_list(context, title, link, description, queryset):
    feed = feedgenerator.Rss201rev2Feed(
        title=title,
        link=link,
        description=description,
        language=u"en")

    for item in queryset:
        url = item.url(context)
        feed.add_item(
            title=item.title,
            link="http://%s/%s" % (context['site_domain'], url),
            description=item.description,
            enclosure=feedgenerator.Enclosure("http://%s/media/%s" % (context['site_domain'], item.audio), str(item.audio.size), mimetypes.guess_type(item.audio.name)[0]),
        )
    return HttpResponse(feed.writeString('UTF-8'), mimetype="application/rss+xml")

# Account
def gen_inv_response(user):
    return { 
        '2': {
            "action_text": "Awaiting Confirmation", 
            "action_href": "", 
            "action_class": "user_add",
            "user_pk": user.pk
        },
        '5': {
            "action_text": "Unfriend", 
            "action_href": reverse('account_friends_remove', kwargs={'user_pk': user.pk}), 
            "action_class": "user_delete",
            "user_pk": user.pk
        },
        '6': {
            "action_text": "Friendship Declined", 
            "action_href": "", 
            "action_class": "user_delete",
            "user_pk": user.pk
        },
        '7': {
            "action_text": "Add Friend", 
            "action_href": reverse('account_friends_add', kwargs={'user_pk': user.pk}),
            "action_class": "user_add",
            "user_pk": user.pk
        },
        'friends': {
            "action_text": "Unfriend", 
            "action_href": reverse('account_friends_remove', kwargs={'user_pk': user.pk}), 
            "action_class": "user_delete",
            "user_pk": user.pk
        },
        'None': {
            "action_text": "Add Friend", 
            "action_href": reverse('account_friends_add', kwargs={'user_pk': user.pk}),
            "action_class": "user_add",
            "user_pk": user.pk
        }
    }

def account_login(request):
    context = RequestContext(request, {})
    next = request.GET.get('next', None)
    if not next:
        next = request.POST.get('next', None)
        
    if request.method == 'POST':
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
                if not next:
                    next = request.META["HTTP_REFERER"]
                    if reverse('account_login') in next:
                        next = reverse("home")
                return HttpResponseRedirect(next)
            else:
                form._errors['username'] = ['Incorrect username or password.',]
    else:
        form = LoginForm()

    context.update({
        'form': form,
        'next': next
    })
    return render_to_response('desktop/content/account/login.html', context)

def account_settings_image(request):
    if not request.user.is_authenticated():
       raise Http404
        
    context = RequestContext(request, {})
    user = request.user
    profile = request.user.profile
        
    if request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            if image:
                profile.image.save(image.name, image)
                profile.save()
    else:
        form = ProfilePictureForm()

    context.update({
        'profile': profile,
        'form': form,
    })
    return render_to_response('desktop/content/account/settings/image.html', context)

def account_settings_details(request):
    """
    TODO: This view seems very flimsy, refactor.
    """
    if not request.user.is_authenticated():
       raise Http404
    
    context = RequestContext(request, {})
    user = request.user
    profile = request.user.profile
        
    if request.method == "POST":
        form = ProfileForm(request.POST)

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
            city = form.cleaned_data['city']
            province = form.cleaned_data['province']
            birth_date_day = form.cleaned_data['birth_date_day']
            birth_date_month = form.cleaned_data['birth_date_month']
            birth_date_year = form.cleaned_data['birth_date_year']
                
            # Create birth_date
            try:
                birth_date = datetime(
                    year=int(birth_date_year),
                    month=int(birth_date_month),
                    day=int(birth_date_day),
                    hour=0,
                    minute=0
                )
            except ValueError:
                birth_date = None

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
            profile.city = city
            profile.province = province
            profile.birth_date = birth_date
   
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
            'city': profile.city,
            'province': province,
        }
        birth_date = profile.birth_date
        if birth_date:
            data.update({
                'birth_date_day': birth_date.day,
                'birth_date_month': birth_date.month,
                'birth_date_year': birth_date.year,
            })
            
        form = ProfileForm(initial=data)

    context.update({
        'form': form,
    })
    return render_to_response('desktop/content/account/settings/details.html', context)

def account_settings_subscriptions(request):
    if not request.user.is_authenticated():
       raise Http404
    
    context = RequestContext(request, {})
    user = request.user
    profile = request.user.profile
        
    if request.method == "POST":
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
    return render_to_response('desktop/content/account/settings/subscriptions.html', context)

@login_required
def account_friends_find(request):
    if request.GET.get('find'):
        q = request.GET['find']
        users = User.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(username__icontains=q)
        ).exclude(pk=request.user.pk)
    else:
        users = []

    # create pager
    page_obj = utils.paging(users, 'page', request, 5)
    users = page_obj.object_list

    return render_to_response('desktop/content/account/friends/find.html', {
        'users': users,
        'page_obj': page_obj,
    }, context_instance=RequestContext(request))

@login_required
def account_friends_add(request, user_pk):
    if not request.is_ajax():
        raise Http404
    
    # get user and create invitation
    user = get_object_or_404(User, pk=user_pk)
    inv = FriendshipInvitation.objects.create_friendship_request(request.user, user)
    inv_response = gen_inv_response(user=user) 
            
    # send confirmation request mail
    message, subject = mailer_friend_request(request=request, from_user=request.user, to_user=user, invitation=inv)
    mail_user(subject, message, user, content_subtype="html", fail_silently=False)
   
    # return json response
    return HttpResponse(simplejson.dumps(inv_response[str(inv.status)]))

@login_required
def account_friends_remove(request, user_pk):
    if not request.is_ajax():
        raise Http404
        
    user = get_object_or_404(User, pk=user_pk)
    Friendship.objects.remove(request.user, user)

    inv_response = gen_inv_response(user=user) 
    return HttpResponse(simplejson.dumps(inv_response[str(None)]))

@login_required
def account_friends_my(request):
    friends = Friendship.objects.friends_for_user(request.user)
    #invitations = FriendshipInvitation.objects.invitations(request.user)
    
    # create pager
    page_obj = utils.paging([friend['friend'] for friend in friends], 'page', request, 5)
    friends = page_obj.object_list

    return render_to_response('desktop/content/account/friends/my.html', {
        'friends': friends,
        'page_obj': page_obj,
        #'invitations': invitations,
    }, context_instance=RequestContext(request))

@login_required
def account_friends_activity(request, user_pk):
    user = get_object_or_404(User, pk = user_pk)
    activity_events = ActivityEvent.objects.filter(user=user).order_by('-timestamp')
    
    # create pager
    page_obj = utils.paging(activity_events, 'page', request, 10)
    object_list = page_obj.object_list

    return render_to_response("desktop/content/account/friends/activity.html", {
        "user": user,
        "object_list": object_list,
        "page_obj": page_obj,
        "show_avatar": False,
    }, context_instance=RequestContext(request))

def account_friends_activity_all(request):
    friends = Friendship.objects.friends_for_user(request.user)
    friends = [o["friend"] for o in friends]
    activity_events = ActivityEvent.objects.filter(user__in=friends).order_by('-timestamp')
    
    # create pager
    page_obj = utils.paging(activity_events, 'page', request, 10)
    object_list = page_obj.object_list

    return render_to_response("desktop/content/account/friends/activity_all.html", {
        "object_list": object_list,
        "page_obj": page_obj,
        "show_avatar": True,
    }, context_instance=RequestContext(request))

@login_required
def account_history(request):
    activity_events = ActivityEvent.objects.filter(user=request.user).order_by('-timestamp')
    
    # create pager
    page_obj = utils.paging(activity_events, 'page', request, 10)
    object_list = page_obj.object_list

    return render_to_response("desktop/content/account/history.html", {
        "object_list": object_list,
        "page_obj": page_obj,
        "show_avatar": False,
    }, context_instance=RequestContext(request))

@login_required
def account_messages_sent(request):
    user = request.user
    object_list = Message.objects.filter(sender=user).order_by('-sent_at')
    context = RequestContext(request, {})
    
    # create pager
    page_obj = utils.paging(object_list, 'page', request, 5)
    object_list = page_obj.object_list
    
    context.update({
        'object_list': object_list,
        'view': 'render_listing_sent',
        'page_obj': page_obj,
    })
    return render_to_response("desktop/content/account/messages/listing.html", context)

@login_required
def account_messages_inbox(request):
    user = request.user
    object_list = Message.objects.filter(thread__users=request.user).exclude(sender=user).order_by('-sent_at')
    context = RequestContext(request, {})
    
    # create pager
    page_obj = utils.paging(object_list, 'page', request, 5)
    object_list = page_obj.object_list
    
    context.update({
        'object_list': object_list,
        'view': 'render_listing_inbox',
        'page_obj': page_obj,
    })
    return render_to_response("desktop/content/account/messages/listing.html", context)

# Chart

class ChartView(object):
    def get_latest_chart(self):
        charts = Chart.permitted.order_by('-modified')
        if not charts:
            raise Http404
        else:
            return charts[0]

    def get_latest_chart_entries(self):
        chart = self.get_latest_chart()
        return chart.chartentries.permitted().order_by('current_position')
    
    def __call__(self, request, template_name='desktop/generic/object_listing_wide.html'):
        queryset=self.get_latest_chart_entries() 
        chart = self.get_latest_chart()
        header = utils.ChartHeader(request, chart)
        queryset_modifiers = [header.page_menu.queryset_modifier,]
        for queryset_modifier in queryset_modifiers:
            queryset = queryset_modifier.updateQuery(queryset)

        return list_detail.object_list(
            request=request,
            queryset=queryset,
            template_name=template_name,
            extra_context={
                'header': header,
            },
        )

# Competitions

def competitions(request, template_name='desktop/generic/object_listing_wide.html'):
    queryset = Competition.permitted.order_by('-created')
    header = utils.CompetitionsHeader(request)

    return list_detail.object_list(
        request=request,
        queryset=queryset,
        template_name=template_name,
        paginate_by=10,
        extra_context={
            'header': header,
        },
    )

def competitions_rules(request):
    context = RequestContext(request, {})
    if not context['settings'].competition_general_rules:
        raise Http404
   
    header = utils.CompetitionsHeader(request)
    context.update({
        'header': header,
    })
    return render_to_response('desktop/content/competitions/rules.html', context)

def competitions_content(request, slug, template_name='desktop/generic/object_detail.html'):
    queryset = Competition.permitted
    header = utils.CompetitionHeader()

    return list_detail.object_detail(
        request=request,
        queryset=queryset,
        slug=slug,
        template_name=template_name,
        extra_context={
            'header': header,
        },
    )

# Events
def events(request):
    context = RequestContext(request, {})
    
    entries = Entry.objects.permitted().by_content_type(Event).order_by('start')
    sorter = utils.EventSorter(entries, 'events', 'by', request)

    entry_dict = {}
    for entry in sorter.object_list:
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start = entry.start.replace(hour=0, minute=0, second=0, microsecond=0)
        if start < now:
            start = now
        end = entry.end
        content = entry.content
        if content:
            content = content.as_leaf_class()
            while start < end:
                if entry_dict.has_key(start):
                    entry_dict[start].append(content)
                else:
                    entry_dict[start] = [content]
                start += timedelta(days=1)
    

    days = entry_dict.keys()
    days.sort()
    entries = []
    for day in days:
        entries.append({'day': day, 'events': entry_dict[day]})
    
    pager = utils.paging(entries, 'page', request, 4)

    context.update({
        'today': date.today(),
        'pager': pager,
        'sorter': sorter,
    })
        
    return render_to_response('desktop/content/events/events.html', context)

def events_content(request, slug):
    content = get_object_or_404(Event, slug=slug, is_public=True)
    context = RequestContext(request, {})
    
    context.update({
        'content': content,
    })
    return render_to_response('desktop/content/events/content.html', context)

# Validate
def validate_username(request):
    if not request.is_ajax():
        raise Http404
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        value = form.fields['username'].widget.value_from_datadict(form.data, form.files, form.add_prefix('username'))
        try:
            form['username'].field.clean(value)
        except ValidationError, e:
            if e.messages:
                response = "'%s'" % str(e.messages[0])
            elif e.message:
                response = ("'%s'" % str(e.message))
            else:
                response = "'Error, please try again'"

            # don't fail if the user already has the username 
            if request.user.is_authenticated():
                user = request.user
                if value == user.username:
                    response = "true" 

            return HttpResponse(response)

        return HttpResponse("true")
    raise Http404

def validate_password(request):
    if not request.is_ajax():
        raise Http404

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        password = form.fields['password'].widget.value_from_datadict(form.data, form.files, form.add_prefix('password'))

        response = "true"
        try:
            form['password'].field.clean(password)
        except ValidationError, e:
            if e.messages:
                response = "'%s'" % str(e.messages[0])
            elif e.message:
                response = ("'%s'" % str(e.message))
            else:
                response = "'Error, please try again'"

        return HttpResponse(response)
    
    raise Http404

def validate_password_confirm(request):
    if not request.is_ajax():
        raise Http404

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        password_confirm = form.fields['password_confirm'].widget.value_from_datadict(form.data, form.files, form.add_prefix('password_confirm'))
        password = form.fields['password'].widget.value_from_datadict(form.data, form.files, form.add_prefix('password'))

        response = "true"
        try:
            form['password_confirm'].field.clean(password_confirm)
            if password != password_confirm:
                response = "'Passwords do not match.'"
                
        except ValidationError, e:
            if e.messages:
                response = "'%s'" % str(e.messages[0])
            elif e.message:
                response = ("'%s'" % str(e.message))
            else:
                response = "'Error, please try again.'"

        return HttpResponse(response)
    
    raise Http404


def validate_captcha(request):
    if not request.is_ajax():
        raise Http404

    if request.method == 'POST':
        if ReCaptcha().verify(request):
            return HttpResponse("true")
        else:
            return HttpResponse("'Incorrect, please try again.'")

    raise Http404

# Galleries
def galleries(request, template_name='desktop/generic/object_listing_block.html'):
    queryset=Gallery.permitted.all()
    header = utils.GalleriesHeader(request)
    queryset_modifiers = [header.page_menu.queryset_modifier,]
    for queryset_modifier in queryset_modifiers:
        queryset = queryset_modifier.updateQuery(queryset)

    return list_detail.object_list(
        request=request,
        queryset=queryset,
        template_name=template_name,
        paginate_by=15,
        extra_context={
            'header': header,
        },
    )

def galleries_content(request, slug, template_name='desktop/generic/object_detail.html'):
    queryset = Gallery.permitted
    header = utils.GalleryHeader()

    return list_detail.object_detail(
        request=request,
        queryset=queryset,
        slug=slug,
        template_name=template_name,
        extra_context={
            'header': header,
        },
    )

# Misc

def contact(request):
    context = RequestContext(request, {})
    form_class = make_contact_form(request)
    sent = False

    if request.method == "POST":
        form = form_class(request.POST)

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
    return render_to_response('desktop/content/contact.html', context)

def comment_add(request):
    """
    Post a comment. Taken from django.contrib.comments.views.comments and adjusted for ajax submition and anonymous users
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email
    
    if not request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = 'Anonymous'
        if not data.get('email', ''):
            data["email"] = 'anonymous@anonymous.com'

    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.get(pk=object_pk)
    except TypeError:
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))

    # Do we want to preview the comment?
    preview = "preview" in data

    # Construct the comment form
    form = comments.get_form()(target, data=data)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % \
                escape(str(form.security_errors())))

    # If there are errors or if we requested a preview show the comment
    if form.errors or preview:
        form.fields['comment'].error_messages['required'] = 'Please enter your comment'
        template_list = [
            "comments/%s_%s_preview.html" % tuple(str(model._meta).split(".")),
            "comments/%s_preview.html" % model._meta.app_label,
            "comments/preview.html",
        ]
        return render_to_response(
            template_list, {
                "comment" : form.data.get("comment", ""),
                "form" : form,
                "instance": target,
                "errors": form.errors
            },
            RequestContext(request, {})
        )

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    for (receiver, response) in responses:
        if response == False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )
    # Ajx additions
    context = RequestContext(request, {})
    context.update({
        'instance': target
    })
    return HttpResponse(CommentsNode('instance').render(context))

#def home(request):
#    context = RequestContext(request, {})
#    return render_to_response('desktop/content/home.html', context)

@cache_for_nginx(60 * 1)
def top_left_right(request, widgets, template='desktop/layout/top_left_right.html'):
    return render_to_response(
        template, 
        widgets, 
        context_instance=RequestContext(request)
    )

def search_results(request):
    context = RequestContext(request, {})
    return render_to_response('desktop/content/search_results.html', context)

def short_redirect(request, pk):
    context = RequestContext(request, {})
    content = get_object_or_404(ContentBase, pk=pk, is_public=True)
    return HttpResponseRedirect(content.url(context))
    
def info_content(request, section):
    context = RequestContext(request, {})
    settings = context['settings']

    # Check is section is valid and has content
    try:
        field = settings._meta.get_field_by_name(section)
    except models.FieldDoesNotExist:
        raise Http404
    
    if not isinstance(field[0], RichTextField):
        raise Http404

    section_verbose_name = field[0].verbose_name
    content = getattr(settings, section)
    if not content:
        raise Http404
        
    menu_items = []
    if settings.about: menu_items.append({'title': 'About Us', 'current': (section == 'about'), 'url': reverse('info_content', kwargs={'section': 'about'})})
    if settings.advertise: menu_items.append({'title': 'Advertise', 'current': (section == 'advertise'), 'url': reverse('info_content', kwargs={'section': 'advertise'})})
    if settings.terms: menu_items.append({'title': 'Terms &amp; Conditions', 'current': (section == 'terms'), 'url': reverse('info_content', kwargs={'section': 'terms'})})
    if settings.privacy: menu_items.append({'title': 'Privacy Policy', 'current': (section == 'privacy'), 'url': reverse('info_content', kwargs={'section': 'privacy'})})
    context.update({
        'content': content,
        'section_verbose_name': section_verbose_name,
        'menu_items': menu_items,
    })
    return render_to_response('desktop/content/info/content.html', context)
    
def handler404(request):
    context = RequestContext(request, {})
    context.update({'error': '404'})
    return render_to_response('desktop/404.html', context)

def handler500(request):
    context = RequestContext(request, {})
    context.update({'error': '500'})
    return render_to_response('desktop/500.html', context)

# Mailers
def mailer_new_user(request, username, password):
    site = Site.objects.get_current()
    host = "http://%s" % request.META['HTTP_HOST']
    subject = render_to_string("desktop/mailers/account/new_user_subject.txt", {'site': site}).strip()
    
    return (render_to_string('desktop/mailers/account/new_user_body.html', {
        'username': username, 
        'password': password,
        'host': host,
        'site': site,
        'mailer_title': 'Welcome',
    }), subject)

def mailer_friend_request(request, from_user, to_user, invitation):
    site = Site.objects.get_current()
    host = "http://%s" % request.META['HTTP_HOST']
    subject = render_to_string("desktop/mailers/account/friend_request_subject.txt", { 'from_user': from_user, 'site': site}).strip()
    
    return (render_to_string('desktop/mailers/account/friend_request_body.html', {
        'host': host,
        'invitation': invitation,
        'site': site,
        'host': "http://%s" % request.META['HTTP_HOST'],
        'mailer_title': 'Friendship Request',
        'from_user': from_user,
        'to_user': to_user
    }), subject)


# Modals
def modals_login(request):
    if not request.is_ajax():
        raise Http404
    
    if request.method == 'POST':
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

    return render_to_response('desktop/modals/login.html', {
        'form': form,
        'FACEBOOK_API_KEY': getattr(settings, "FACEBOOK_API_KEY", None),
    })

def modals_content(request, slug):
    if not request.is_ajax():
        raise Http404
    
    context = RequestContext(request, {})
    
    content = get_object_or_404(ContentBase, slug=slug, is_public=True)
    content = content.as_leaf_class()

    return content.render_modals_content(context)

def modals_register(request):
    if not request.is_ajax():
        raise Http404
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            # Get cleaned form values
            username = form.cleaned_data['username']
            email_address = form.cleaned_data['email_address']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email_subscribe = form.cleaned_data['email_subscribe']
            sms_subscribe = form.cleaned_data['sms_subscribe']

            # Generate Random Password
            password = auth.models.UserManager().make_random_password(length=8)

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
            profile.email_subscribe = email_subscribe
            profile.sms_subscribe = sms_subscribe
            profile.save()
       
            # Send confirmation mail
            message, subject = mailer_new_user(request, username, password)
            mail_user(subject, message, user, content_subtype="html", fail_silently=False)
            
            # Authenticate and login user
            user = auth.authenticate(
                username=username, 
                password=password
            )
            if user:
                auth.login(request, user)
            
            return HttpResponse("true")
        else:
            return HttpResponse("false")
    else:
        form = RegistrationForm()
    
    context = RequestContext(request, {})
    context.update({
        'form': form,
    })
    return render_to_response('desktop/modals/register.html', context)

def modals_password_reset(request):
    if not request.is_ajax():
        raise Http404

    context = {}
    return render_to_response('desktop/modals/password_reset.html', context)

# News
def news(request, template_name='desktop/generic/object_listing_wide.html'):
    news_label = Label.objects.get(title__iexact='news')
    queryset=Post.permitted.filter(labels=news_label)
    header = utils.NewsHeader(request)
    queryset_modifiers = [header.page_menu.queryset_modifier,]
    for queryset_modifier in queryset_modifiers:
        queryset = queryset_modifier.updateQuery(queryset)

    return list_detail.object_list(
        request=request,
        queryset=queryset,
        template_name=template_name,
        paginate_by=10,
        extra_context={
            'header': header,
        },
    )

def news_content(request, slug, template_name='desktop/generic/object_detail.html'):
    queryset = ContentBase.permitted
    header = utils.NewsArticleHeader()

    return list_detail.object_detail(
        request=request,
        queryset=queryset,
        slug=slug,
        template_name=template_name,
        extra_context={
            'header': header,
        },
    )

# Popups     
def listen_live(request):
    context = RequestContext(request, {})
    return render_to_response('desktop/popups/listen_live.html', context)

def studio_cam(request):
    context = RequestContext(request, {})
    settings = context['settings']
    urls = settings.studio_cam_urls
    if urls:
        urls = urls.replace('\r', '').split('\n')
    else:
        urls = []

    context.update({
        'urls': urls,
    })

    return render_to_response('desktop/popups/studio_cam.html', context)

# Podcasts
def podcasts_rss(request):
    context = RequestContext(request, {})
    title = "%s Podcasts" % context['site_name']
    link = reverse('home')
    description = "Latest podcasts for %s." % context['site_name']
    queryset = PodcastStandalone.permitted.order_by("-created")
    return rss_object_list(context, title, link, description, queryset)

# Reviews
def reviews(request, template_name='desktop/generic/object_listing_wide.html'):
    reviews_label = Label.objects.get(title__iexact='reviews')
    queryset=Post.permitted.filter(labels=reviews_label)
    header = utils.ReviewsHeader(request, reviews_label)
    queryset_modifiers = [header.page_menu.queryset_modifier,]
    for queryset_modifier in queryset_modifiers:
        queryset = queryset_modifier.updateQuery(queryset)

    return list_detail.object_list(
        request=request,
        queryset=queryset,
        template_name=template_name,
        paginate_by=10,
        extra_context={
            'header': header,
        },
    )

def reviews_content(request, slug, template_name='desktop/generic/object_detail.html'):
    queryset = ContentBase.permitted
    header = utils.ReviewsArticleHeader()

    return list_detail.object_detail(
        request=request,
        queryset=queryset,
        slug=slug,
        template_name=template_name,
        extra_context={
            'header': header,
        },
    )

# Shows
class ShowsLineUp(object):
    def __call__(self, request, template_name='desktop/generic/object_listing_block.html'):
        queryset = Entry.objects.permitted().by_content_type(Show).order_by('start')
        header = utils.ShowsHeader(request)
        queryset_modifiers = [header.page_menu.queryset_modifier,]
        for queryset_modifier in queryset_modifiers:
            queryset = queryset_modifier.updateQuery(queryset)

        return list_detail.object_list(
            request=request,
            queryset=queryset,
            template_name=template_name,
            extra_context={
                'header': header,
            },
        )

def shows_dj_appearances(request, slug):
    castmember = get_object_or_404(CastMember, slug=slug, is_public=True)
    context = RequestContext(request, {})
    header = utils.CastMemberHeader(request, castmember)

    appearances = Appearance.objects.permitted().filter(castmember=castmember)
    events = [appearance.event for appearance in appearances]
    entries = Entry.objects.permitted().filter(content__in=events).order_by('start')
   
    entry_dict = {}
    for entry in entries:
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start = entry.start.replace(hour=0, minute=0, second=0, microsecond=0)
        if start < now:
            start = now
        end = entry.end
        content = entry.content
        if content:
            content = content.as_leaf_class()
            while start < end:
                if entry_dict.has_key(start):
                    entry_dict[start].append(content)
                else:
                    entry_dict[start] = [content]
                start += timedelta(days=1)
    

    days = entry_dict.keys()
    days.sort()
    entries = []
    for day in days:
        entries.append({'day': day, 'events': entry_dict[day]})
    
    # create pager
    page_obj = utils.paging(entries, 'page', request, 5)
    object_list = page_obj.object_list

    context.update({
        'today': date.today(),
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'object_list': object_list,
        'header': header
    })
    return render_to_response('desktop/content/shows/dj_appearances.html', context)

def shows_dj_blog(request, slug, template_name='desktop/generic/object_listing_wide.html'):
    castmember = get_object_or_404(CastMember, slug=slug, is_public=True)
    owner = castmember.owner 
    queryset = ContentBase.permitted.filter(owner=owner).exclude(classname__in=['PodcastStandalone', 'CastMember', 'Show']).order_by("-created") if owner else []
    header = utils.CastMemberHeader(request, castmember)

    return list_detail.object_list(
        request=request,
        queryset=queryset,
        template_name=template_name,
        paginate_by=10,
        extra_context={
            'header': header,
        },
    )

def shows_dj_podcasts(request, slug, template_name='desktop/content/shows/dj_podcasts.html'):
    castmember = get_object_or_404(CastMember, slug=slug, is_public=True)
    owner = castmember.owner 
    queryset = PodcastStandalone.permitted.filter(owner=owner).order_by("-created") if owner else []
    header = utils.CastMemberHeader(request, castmember)

    return list_detail.object_list(
        request=request,
        queryset=queryset,
        template_name=template_name,
        paginate_by=10,
        extra_context={
            'castmember': castmember,
            'header': header,
        },
    )

def shows_dj_podcasts_content(request, castmember_slug, podcast_slug, template_name='desktop/generic/object_detail.html'):
    castmember = get_object_or_404(CastMember, slug=castmember_slug, is_public=True)
    queryset = ContentBase.permitted
    header = utils.CastMemberHeader(request, castmember)

    return list_detail.object_detail(
        request=request,
        queryset=queryset,
        slug=podcast_slug,
        template_name=template_name,
        extra_context={
            'header': header,
        },
    )

def shows_dj_podcasts_rss(request, slug):
    castmember = get_object_or_404(CastMember, slug=slug, is_public=True)
    owner = castmember.owner 
    context = RequestContext(request, {})
    queryset = PodcastStandalone.permitted.filter(owner=owner).order_by("-created") if owner else []
    title = "%s Podcasts" % context['site_name']
    link = reverse('shows_dj_podcasts', kwargs={'slug': castmember.slug})
    description = "Latest podcasts for %s." % castmember.title
    return rss_object_list(context, title, link, description, queryset)

def shows_dj_contact(request, slug):
    castmember = get_object_or_404(CastMember, slug=slug, is_public=True)
    header = utils.CastMemberHeader(request, castmember)
    context = RequestContext(request, {})
    form_class = make_contact_form(request, base_class=_BaseCastmemberContactForm)
    sent = False

    if request.method == "POST":
        form = form_class(data=request.POST, castmember=castmember)

        if form.is_valid(request):
            form.send_message()
            sent = True
    else:
        form = form_class(castmember=castmember)
        
    context.update({
        'castmember': castmember,
        'header': header,
        'form': form,
        'sent': sent,
    })
    return render_to_response('desktop/content/shows/dj_contact.html', context)

def shows_dj_profile(request, slug):
    castmember = get_object_or_404(CastMember, slug=slug, is_public=True)
    context = RequestContext(request, {})

    header = utils.CastMemberHeader(request, castmember)
    context.update({
        'header': header,
        'castmember': castmember,
    })
    return render_to_response('desktop/content/shows/dj_profile.html', context)

def shows_dj_content(request, castmember_slug, content_slug, template_name='desktop/generic/object_detail.html'):
    castmember = get_object_or_404(CastMember, slug=castmember_slug, is_public=True)
    queryset = ContentBase.permitted
    header = utils.CastMemberHeader(request, castmember)

    return list_detail.object_detail(
        request=request,
        queryset=queryset,
        slug=content_slug,
        template_name=template_name,
        extra_context={
            'header': header,
        },
    )

def shows_dj_appearances_content(request, castmember_slug, content_slug, template_name='desktop/generic/object_detail.html'):
    return shows_dj_content(request, castmember_slug, content_slug, template_name)

# Model Views
class CodeBannerViews(object):
    def render(self):
        return render_to_string('desktop/content/banners/code_banner.html', {"self": self})

class ImageBannerViews(object):
    def render(self):
        return render_to_string('desktop/content/banners/image_banner.html', {"self": self})

    def get_context_url(self, context):
        return self.url

class ContentBaseViews(object):
    def render_updates(self, context):
        context = {
            'object': self,
            'url': self.url(context),
            'node': context['node'],
        }
        return render_to_string('desktop/content/contentbase/updates.html', context)
    
    def render_updates_featured(self, context):
        context = {
            'object': self,
            'url': self.url(context),
        }
        return render_to_string('desktop/content/contentbase/updates_featured.html', context)
   
    def render_updates_widget(self, context):
        labels = self.labels.visible()
        label = labels[0] if labels else None
        context = {
            'self': self,
            'label': label,
            'url': self.url(context),
        }
        return render_to_string('desktop/content/contentbase/updates_widget.html', context)
   
    def render_modals_content(self, context):
        context.update({
            'self': self,
        })
        return render_to_response('desktop/content/contentbase/modals_content.html', context)
    
    def render_block(self, context):
        context = {
            'object': self,
            'url': self.url(context),
        }
        return render_to_string('desktop/content/contentbase/block.html', context)
        
    def render_listing(self, context):
        context = {
            'self': self,
            'url': self.url(context),
        }
        return render_to_string('desktop/content/contentbase/listing.html', context)

    def render_article(self, context):
        context = RequestContext(context['request'], {})
        context.update({
            'self': self,
        })
        return render_to_string('desktop/content/article.html', context)
        
    def url(self, context):
        def handle_home(self):
            return None

        def handle_shows(self):
            owner = self.owner
            if owner:
                castmembers = CastMember.permitted.filter(owner=owner)
                if castmembers:
                    if self.classname in ['PodcastStandalone',]:
                        return reverse('shows_dj_podcasts_content', kwargs={'castmember_slug': castmembers[0].slug, 'podcast_slug': self.slug})
                    else:
                        return reverse('shows_dj_content', kwargs={'castmember_slug': castmembers[0].slug, 'content_slug': self.slug})
                elif self.classname in ['Event',]:
                    castmembers = self.as_leaf_class().castmembers.permitted()
                    return reverse('shows_dj_appearances_content', kwargs={'castmember_slug': castmembers[0].slug, 'content_slug': self.slug})
        
        def handle_galleries(self):
            if self.classname in ['Gallery',]:
                return reverse('galleries_content', kwargs={'slug': self.slug})
        
        def handle_competitions(self):
            if self.classname in ['Competition',]:
                return reverse('competitions_content', kwargs={'slug': self.slug})
        
        def handle_chart(self):
            if self.classname in ['Chart',]:
                return reverse('chart', kwargs={'slug': self.slug})
        
        def handle_events(self):
            if self.classname in ['Event',]:
                return reverse('events_content', kwargs={'slug': self.slug})
        
        def handle_news(self):
            return reverse('news_content', kwargs={'slug': self.slug})
        
        def handle_reviews(self):
            return reverse('reviews_content', kwargs={'slug': self.slug})

        section_handlers = [
            ('home', handle_home),
            ('shows', handle_shows),
            ('galleries', handle_galleries),
            ('competitions', handle_competitions),
            ('events', handle_events),
            ('chart', handle_chart),
            ('news', handle_news),
            ('reviews', handle_reviews),
        ]

        try:
            section = context['section']
        except KeyError:
            section = 'home'

        for section_handler in section_handlers:
            if section == section_handler[0]:
                url = section_handler[1](self)
        if url:
            return url
        else:
            for section_handler in section_handlers:
                url = section_handler[1](self)
                if url:
                    return url
            
        return '/404'

    def post_head(self, context):
        # create a short sharing url
        host = "http://%s" % context['request'].META['HTTP_HOST']
        share_url = "%s/%s" % (host, self.pk)

        # get site name
        current_site = Site.objects.get_current()
        site_name = current_site.name
        
        # build mailto url
        mailto_url = "mailto:?%s" % urlencode({
            'subject': "%s: %s" % (site_name, self.title),
            'body': """I wanted to share this story with you: %s
---
%s
%s""" % (share_url, self.title, self.description),
        })
        mailto_url = mailto_url.replace('+', ' ')

        # build facebook url
        facebook_url = "http://www.facebook.com/sharer.php?%s" % urlencode({'u': share_url})

        # build twitter url
        twitter_status = "RT %s" % self.title
        twitter_status = "%s...: %s" % (twitter_status[:140 - len(share_url) - 5], share_url)
        twitter_url = "http://twitter.com/home?%s" % urlencode({
            'status': twitter_status,
            'source': site_name
        })

        context.update({
            'instance': self,
            'owner': self.owner,
            'host': host,
            'share_url': share_url,
            'mailto_url': mailto_url,
            'facebook_url': facebook_url,
            'twitter_url': twitter_url,
        })
        return render_to_string('desktop/content/contentbase/post_head.html', context)

class ChartEntryViews(object):
    def render_listing(self, context):
        song = self.song
        now = datetime.now()
        week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        
        days_on = (week_start - self.created).days
        if days_on > 0:
            weeks_on = days_on / 7
        else:
            weeks_on = 0

        context.update({
            'self': self, 
            'song': self.song,
            'artist': song.get_primary_artist(),
            'weeks_on': weeks_on,
        })
        return render_to_string('desktop/content/charts/entry.html', context)
    
class CompetitionViews(object):
    def render_listing(self, context):
        context = {
            'self': self,
            'url': self.url(context),
        }
        return render_to_string('desktop/content/competitions/listing.html', context)
    
    def render_article_body(self, context):
        form_class = make_competition_form(self)
        
        request = context['request']
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                form.create_entry(self, request.user)
        else:
            form = form_class()

        context.update({
            'self': self,
            'form': form,
        })
        return render_to_string('desktop/content/competitions/article_body.html', context)

class EntryViews(object):
    def render_block(self, context):
        content = self.content.as_leaf_class()
        credits = content.credits.order_by('role')
        castmember_url = credits[0].castmember.url() if credits else ''

        context = {
            'self': self,
            'content': content,
            'castmember_url': castmember_url,
        }
        return render_to_string('desktop/content/entry/block.html', context)

class EventViews(object):
    def render_article_body(self, context):
        entries = Entry.objects.permitted().upcoming().filter(content=self).order_by('start')
        context = {
            'self': self,
            'entries': entries,
        }
        return render_to_string('desktop/content/events/article_body.html', context)
    
    def render_listing(self, context):
        locations = self.locations.permitted()
        location = locations[0] if locations else None
        
        context = {
            'self': self,
            'url': self.url(context),
            'location': location,
        }
        return render_to_string('desktop/content/events/listing.html', context)
    
class GalleryViews(object):
    def render_block(self, context):
        context = {
            'self': self,
            'url': self.url(context),
        }
        return render_to_string('desktop/content/galleries/block.html', context)
    
    def render_article_body(self, context):
        context = {
            'self': self,
        }
        return render_to_string('desktop/content/galleries/article_body.html', context)

class CastMemberViews(object):
    def url(self, context=None):
        return reverse('shows_dj_blog', kwargs={'slug': self.slug})

class PostViews(object):
    def render_article_body(self, context):
        context = {
            'self': self,
        }
        return render_to_string('desktop/content/posts/article_body.html', context)

class PodcastStandaloneViews(object):
    def render_article_body(self, context):
        castmember = CastMember.objects.filter(owner=self.owner)
        context.update({
            'self': self,
            'castmember': castmember[0] if castmember else None,
        })
        return render_to_string('desktop/content/podcaststandalone/article_body.html', context)
       
class UserViews(object):
    def url(self):
        castmembers = self.contentbase_set.permitted().filter(classname__exact="castmember")
        return castmembers[0].as_leaf_class().url() if castmembers else ''

    def render_listing(self, context):
        request = context['request']
        
        are_friends = Friendship.objects.are_friends(self, request.user)
        if are_friends:
            status = 'friends'
        else:
            status = str(FriendshipInvitation.objects.invitation_status(self, request.user))
  
        inv_response = gen_inv_response(user = self)

        update_count = StatusUpdate.objects.filter(user=self).count()
        like_count = Vote.objects.filter(user=self).count()
        comment_count = Comment.objects.filter(user=self).count()
        context = {
            'user': self,
            'profile': self.profile,
            'update_count': update_count,
            'like_count': like_count,
            'comment_count': comment_count,
        }

        context.update(inv_response[status])

        return render_to_string('desktop/content/user/listing.html', context)
    
    def render_block(self, context):
        request = context['request']
        
        are_friends = Friendship.objects.are_friends(self, request.user)
        if are_friends:
            status = 'friends'
        else:
            status = str(FriendshipInvitation.objects.invitation_status(self, request.user))
  
        inv_response = gen_inv_response(user = self)

        update_count = StatusUpdate.objects.filter(user=self).count()
        like_count = Vote.objects.filter(user=self).count()
        comment_count = Comment.objects.filter(user=self).count()
        context = {
            'user': self,
            'profile': self.profile,
            'update_count': update_count,
            'like_count': like_count,
            'comment_count': comment_count,
        }

        context.update(inv_response[status])

        return render_to_string('desktop/content/user/block.html', context)

class SongViews(object):
    def render_modals_content(self, context):
        context.update({
            'self': self,
            'artist': self.get_primary_artist(),
        })
        return render_to_response('desktop/content/charts/modals_content.html', context)
   
class StatusUpdateViews(object):
    def render_updates(self, context):
        user = self.user
        user_twitter_username = user.profile.twitter_username
        
        # build retweet url
        credit = "@%s" % user_twitter_username if user_twitter_username else ""
        status = "RT "
        if credit:
            status += "%s " % credit
        status += self.text
        status = status[:140]
        retweet_url = "http://twitter.com/home?%s" % urlencode({
            'status': status,
        })
        
        # determine if the update is from a castmember (user with credit of role 1)
        castmember = False
        castmembers = CastMember.objects.filter(owner=user)
        if castmembers:
            castmember = castmembers[0] if Credit.objects.filter(castmember=castmembers[0], role__exact='1') else False

        context = {
            'request': context['request'],
            'object': self,
            'user': user,
            'profile': user.profile,
            'retweet_url': retweet_url, 
            'castmember': castmember,
        }
        return render_to_string('desktop/content/status_update/update.html', context)
        
    def render_activity_listing(self, context, activity):
        context.update({
            'object': self,
            'activity': activity,
        })
        return render_to_string('desktop/content/status_update/activity_listing.html', context)

class MessageViews(object):
    def render_listing_sent(self, context):
        thread = self.thread
        users = thread.users.exclude(pk=self.sender.pk).order_by('username')
        profile = users[0].profile
        context = {
            'object': self,
            'thread': thread,
            'users': users,
            'profile': profile,
        }
        return render_to_string('desktop/content/message/listing_sent.html', context)
    
    def render_listing_inbox(self, context):
        thread = self.thread
        sender = self.sender
        profile = sender.profile
        context = {
            'object': self,
            'thread': thread,
            'sender': sender,
            'profile': profile,
        }
        return render_to_string('desktop/content/message/listing_inbox.html', context)
    
    def render_listing_thread(self, context):
        thread = self.thread
        sender = self.sender
        profile = sender.profile
        context = {
            'object': self,
            'thread': thread,
            'sender': sender,
            'profile': profile,
        }
        return render_to_string('desktop/content/message/listing_thread.html', context)
       
class ActivityEventViews(object):
    def render_listing(self, context):
        return self.content_object.render_activity_listing(context, self)

class VoteViews(object):
    def render_activity_listing_status_update(self, context, activity):
        content = self.object
        context.update({
            'content': content,
            'activity': activity,
            'user': content.user,
        })
        return render_to_string('desktop/content/vote/activity_listing_status_update.html', context)
        
    def render_activity_listing(self, context, activity):
        content = self.object
        if isinstance(content, StatusUpdate):
            return self.render_activity_listing_status_update(context, activity)        
        else:
            content_url = content.url(context)
            content_section = determine_section(content_url)
            context.update({
                'activity': activity,
                'content': content,
                'content_url': content_url,
                'content_section': content_section,
            })
            return render_to_string('desktop/content/vote/activity_listing.html', context)

class CommentViews(object):
    def render_activity_listing(self, context, activity):
        content = self.content_object
        content_url = content.url(context)
        context.update({
            'object': self,
            'activity': activity,
            'content': content,
            'content_url': content_url,
        })
        return render_to_string('desktop/content/comment/activity_listing.html', context)
    
public.site.register(CastMember, CastMemberViews)
public.site.register(ChartEntry, ChartEntryViews)
public.site.register(CodeBanner, CodeBannerViews)
public.site.register(ContentBase, ContentBaseViews)
public.site.register(Competition, CompetitionViews)
public.site.register(Entry, EntryViews)
public.site.register(Event, EventViews)
public.site.register(Gallery, GalleryViews)
public.site.register(ImageBanner, ImageBannerViews)
public.site.register(Post, PostViews)
public.site.register(PodcastStandalone, PodcastStandaloneViews)
public.site.register(User, UserViews)
public.site.register(Song, SongViews)
public.site.register(StatusUpdate, StatusUpdateViews)
public.site.register(Message, MessageViews)
public.site.register(ActivityEvent, ActivityEventViews)
public.site.register(Vote, VoteViews)
public.site.register(Comment, CommentViews)
