from datetime import datetime
import inspect, sys
import random
        

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.contrib.auth.models import User
from django.contrib.auth.views import password_reset_confirm
from django.db import models
from django.db.models.query import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.generic import list_detail

from facebookconnect.models import FacebookProfile
from friends.models import Friendship
from user_messages.models import Message
from user_messages.forms import MessageReplyForm
from user_messages.models import Thread

from broadcastcms.activity.models import ActivityEvent
from broadcastcms.base.models import ModelBase, ContentBase
from broadcastcms.calendar.models import Entry
from broadcastcms.competition.models import Competition
from broadcastcms.event.models import Event
from broadcastcms.label.models import Label
from broadcastcms.lite.desktop_urls import urlpatterns
from broadcastcms.lite.forms import FacebookRegistrationForm, LoginForm
from broadcastcms.post.models import Post
from broadcastcms.radio.models import Song
from broadcastcms.show.models import Credit, Show
from broadcastcms.status.models import StatusUpdate
from broadcastcms.lite import utils
from broadcastcms.lite.forms import NewMessageFormMultipleFriends
        
from utils import SSIContentResolver

VIEW_CHOICES = []
for pattern in urlpatterns:
    try:
        VIEW_CHOICES.append((pattern.name, pattern.name.title().replace('_', ' ')))
    except AttributeError:
        pass

VIEW_CHOICES = tuple(VIEW_CHOICES)

class Widget(SSIContentResolver, ModelBase):
    title = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.title
        
    def get_ssi_url(self, request=None):
        return reverse('ssi_widget', kwargs={'slug': self.slug})

class AccountMenuWidget(Widget):
    user_unique = True
    login_required = True
    
    class Meta():
        verbose_name = 'Account Menu Widget'
        verbose_name_plural = 'Account Menu Widgets'
   
    def render_content(self, context, section):
        from user_messages.models import Thread
        request = context['request']
        
        messages = Thread.objects.unread(request.user).count()
        msg = "Messages"
        if messages:
            msg += " (%s)" % messages

        menu_items = [
            {
                'title': msg,
                'section': 'messages',
                'url': reverse('messages_inbox'),
            },
            {
                'title': 'History',
                'section': 'history',
                'url': reverse('account_history'),
            },
            {
                'title': 'Friends',
                'section': 'friends',
                'url': reverse('account_friends_my'),
            },
            {
                'title': 'Settings',
                'section': 'settings',
                'url': reverse('account_settings_details'),
            },
        ]
        profile = request.user.profile

        context.update({
            'menu_items': menu_items,
            'account_section': section,
            'profile': profile,
        })
        return render_to_string('widgets/widgets/account_menu.html', context)
    
    def get_ssi_url(self, request):
        section = request.path.split('/')[2]
        return reverse('ssi_account_menu_widget', kwargs={'slug': self.slug, 'section': section})

class BannerWidget(Widget):
    width = models.IntegerField()
    height = models.IntegerField()
    content = models.ForeignKey(
        ContentBase,
        limit_choices_to = ~Q(classname__in=['PromoWidget', 'PromoWidgetSlot', 'ModelBase', 'ContentBase',]) & Q(is_public=True),
        related_name="banner_widget_content",
    )
    
    class Meta():
        verbose_name = 'Banner Widget'
        verbose_name_plural = 'Banner Widgets'

    def render_content(self, context, *args, **kwargs):
        context = {
            'widget': self,
            'content': self.content.as_leaf_class(),
        }
        return render_to_string('widgets/widgets/banner.html', context)

class CreateMessageWidget(Widget):
    user_unique = True
    login_required = True
    receive_post = True
    
    class Meta():
        verbose_name = 'Create Message Widget'
        verbose_name_plural = 'Create Message Widgets'
    
    def render_content(self, context, *args, **kwargs):
        request = context['request']
        form_class= NewMessageFormMultipleFriends
        multiple=True
        user_id=None
        
        if user_id is not None:
            user_id = [int(user_id)]
        elif 'to_user' in request.GET and request.GET['to_user'].isdigit():
            to_users = request.POST['to_user']
            user_id = map(int, request.GET.getlist('to_user'))
        if not multiple and user_id:
            user_id = user_id[0]
        initial = {'to_user': user_id}
        if request.method == 'POST':

            """
            Because of the way the js autobox works we can only send through usernames
            as to_user values. So we need to convert posted usernames into valid user pks.
            We do not convert invalid usernames but keep them as is to trigger failure 
            during validation. Because we are altering the POST querydict in username to 
            pk conversion, we have to reset POST to the original qd in case of validation errors.
            """
            original_qd = request.POST.__copy__()
            
            if request.POST.has_key('to_user'):
                friend_pks = [friend['friend'].pk for friend in Friendship.objects.friends_for_user(request.user)]

                to_users = request.POST.getlist('to_user')
                qs = User.objects.filter(username__in=to_users, pk__in=friend_pks).order_by('username')

                valid_pks = []
                valid_usernames = []
                for user in qs:
                    valid_pks.append(user.pk)
                    valid_usernames.append(user.username)
                    
                invalid_usernames = []
                for username in to_users:
                    if username not in valid_usernames:
                        invalid_usernames.append(username)


                to_users = [user.pk for user in qs] + invalid_usernames
                new_qd = request.POST.__copy__()
                new_qd.setlist('to_user', to_users)
                request.POST = new_qd

            form = form_class(request.POST, user=request.user, initial=initial)
            if form.is_valid():
                msg = form.save()
                return HttpResponseRedirect(msg.get_absolute_url())
            else:
                form.data = original_qd
                
        else:
            form = form_class(user=request.user, initial=initial)

        return render_to_string('widgets/widgets/create_message.html', {
            'form': form
        }, context_instance=RequestContext(request))

class EmbedWidget(Widget):
    code = models.TextField(help_text='The full HTML/Javascript code snippet to be embedded.')
    
    class Meta():
        verbose_name = 'Embed Widget'
        verbose_name_plural = 'Embed Widgets'

    def render_content(self, context, *args, **kwargs):
        context = {
            'widget': self,
        }
        return render_to_string('widgets/widgets/embed.html', context)

class FacebookSetupWidget(Widget):
    class Meta():
        verbose_name = 'Facebook Setup Widget'
        verbose_name_plural = 'Facebook Setup Widgets'
    
    def render_content(self, context, *args, **kwargs):
        """
        This is a customization of facebookconnect.views.setup to suit our particular needs
        """
        request = context['request']
        redirect_url = None

        #you need to be logged into facebook.
        if not request.facebook.uid:
            url = reverse('account_login')
            if request.REQUEST.get(REDIRECT_FIELD_NAME,False):
                url += "?%s=%s" % (REDIRECT_FIELD_NAME, request.REQUEST[REDIRECT_FIELD_NAME])
            return HttpResponseRedirect(url)

        #setup forms
        login_form = LoginForm()
        registration_form = FacebookRegistrationForm()

        #figure out where to go after setup
        if request.REQUEST.get(REDIRECT_FIELD_NAME,False):
            redirect_url = request.REQUEST[REDIRECT_FIELD_NAME]
        elif redirect_url is None:
            redirect_url = getattr(settings, "LOGIN_REDIRECT_URL", "/")

        #check that this fb user is not already in the system
        try:
            FacebookProfile.objects.get(facebook_id=request.facebook.uid)
            # already setup, move along please
            return HttpResponseRedirect(redirect_url)
        except FacebookProfile.DoesNotExist, e:
            # not in the db, ok to continue
            pass

        #user submitted a form - which one?
        if request.method == "POST":
            # user setup his/her own local account in addition to their facebook
            # account. The user will have to login with facebook unless they 
            # reset their password.
            if request.POST.get('register',False):
                profile = FacebookProfile(facebook_id=request.facebook.uid)
                fname = lname = ''
                if profile.first_name != "(Private)":
                    fname = profile.first_name
                if profile.last_name != "(Private)":
                    lname = profile.last_name
                user = User(first_name=fname, last_name=lname)
                registration_form = FacebookRegistrationForm(
                                            data=request.POST, instance=user)
                if registration_form.is_valid():
                    user = registration_form.save()
                    profile.user = user
                    profile.save()
                    login(request, authenticate(request=request))
                    return HttpResponseRedirect(redirect_url)
            
            #user logs in in with an existing account, and the two are linked.
            elif request.POST.get('login',False):
                login_form = LoginForm(data=request.POST)

                if login_form.is_valid():
                    username = login_form.cleaned_data['username']
                    password = login_form.cleaned_data['password']
                    user = authenticate(username=username, password=password)
                    if user and user.is_active:
                        FacebookProfile.objects.get_or_create(user=user, facebook_id=request.facebook.uid)
                        login(request, user)
                        return HttpResponseRedirect(redirect_url)
                    else:
                        login_form._errors['username'] = ['Incorrect username or password.',]
    
        #user didn't submit a form, but is logged in already. We'll just link up their facebook
        #account automatically.
        elif request.user.is_authenticated():
            try:
                request.user.facebook_profile
            except FacebookProfile.DoesNotExist:
                profile = FacebookProfile(facebook_id=request.facebook.uid)
                profile.user = request.user
                profile.save()

            return HttpResponseRedirect(redirect_url)
    
        # user just showed up
        else:
            request.user.facebook_profile = profile = FacebookProfile(facebook_id=request.facebook.uid)
            login_form = LoginForm()
            fname = lname = ''
            if profile.first_name != "(Private)":
                fname = profile.first_name
            if profile.last_name != "(Private)":
                lname = profile.last_name
            user = User(first_name=fname, last_name=lname)
            registration_form = FacebookRegistrationForm(instance=user)
    
    
        template_dict = {
            "login_form": login_form,
            "registration_form": registration_form
        }
    
        # we only need to set next if its been passed in the querystring or post vars
        if request.REQUEST.get(REDIRECT_FIELD_NAME, False):
            template_dict.update( {REDIRECT_FIELD_NAME: request.REQUEST[REDIRECT_FIELD_NAME]})
        
        return render_to_string('widgets/widgets/facebook_setup.html', template_dict, context_instance=context)

class FriendsWidget(Widget):
    user_unique = True
    login_required = True
    
    class Meta():
        verbose_name = 'Friends Widget'
        verbose_name_plural = 'Friends Widgets'
    
    def render_content(self, context, *args, **kwargs):
        from friends.models import Friendship
        from broadcastcms.lite import utils

        request = context['request']

        friends = Friendship.objects.friends_for_user(request.user)
    
        # create pager
        page_obj = utils.paging([friend['friend'] for friend in friends], 'page', request, 6)
        friends = page_obj.object_list

        context = {
            'friends': friends,
            'page_obj': page_obj,
            'request': request,
        }
        return render_to_string('widgets/widgets/friends.html', context)

class FriendsActivityWidget(Widget):
    user_unique = True
    login_required = True
    
    class Meta():
        verbose_name = 'Friends Activity Widget'
        verbose_name_plural = 'Friends Activity Widgets'
    
    def render_content(self, context, user_pk=None, *args, **kwargs):
        request = context['request']

        # if we have a user pk list activities for that user only,
        # otherwise list activities for all friends
        user = None
        if user_pk:
            user = get_object_or_404(User, pk = user_pk)
            activity_events = ActivityEvent.objects.filter(user=user).order_by('-timestamp')
        else:
            friends = Friendship.objects.friends_for_user(request.user)
            friends = [o["friend"] for o in friends]
            activity_events = ActivityEvent.objects.filter(user__in=friends).order_by('-timestamp')
    
        # create pager
        page_obj = utils.paging(activity_events, 'page', request, 10)
        object_list = page_obj.object_list

        return render_to_string("widgets/widgets/friends_activity.html", {
            'user': user,
            "object_list": object_list,
            "page_obj": page_obj,
            "show_avatar": not user,
        }, context_instance=RequestContext(request))

class FriendsFindWidget(Widget):
    user_unique = True
    login_required = True

    class Meta():
        verbose_name = 'Find Friends Widget'
        verbose_name_plural = 'Find Friends Widgets'
   
    def render_content(self, context, *args, **kwargs):
        request = context['request']

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

        return render_to_string('widgets/widgets/friends_find.html', {
            'users': users,
            'page_obj': page_obj,
        }, context_instance=RequestContext(request))

class FriendsFacebookInviteWidget(Widget):
    user_unique = True
    login_required = True
    receive_post = True

    class Meta():
        verbose_name = 'Invite Facebook Friends Widget'
        verbose_name_plural = 'Invite Facebook Friends Widgets'
   
    def render_content(self, context, *args, **kwargs):
        request = context['request']

        template_dict = {}
        if request.method == "POST":
            fb_ids = request.POST.getlist("ids")
            for fb_id in fb_ids:
                FacebookFriendInvite.objects.create(user=request.user,
                    fb_user_id=fb_id)
            template_dict.update({
                'invited': True
            })
        return render_to_string(
            "widgets/widgets/friends_facebook_invite.html", 
            template_dict, 
            context_instance=RequestContext(request)
        )

class FriendsSideNavWidget(Widget):
    class Meta():
        verbose_name = 'Friends Side Navigation Widget'
        verbose_name_plural = 'Friends Side Navigation Widgets'
    
    def render_content(self, context, *args, **kwargs):
        items = [{
                'title': 'My Friends',
                'section': 'my',
                'class': 'see_my_friends',
                'url': reverse('account_friends_my'),
            },
            {
                'title': "See My Friends' Recent Activity",
                'section': 'activity',
                'class': 'friends_activity',
                'url': reverse('account_friends_activity_all'),
            },
            {
                'title': "Find More Friends",
                'section': 'find',
                'class': 'more_friends',
                'url': reverse('account_friends_find'),
            },
        ]

        context = {
            'widget': self,
            'items': items,
            'active_section': context['request'].path.split('/')[3],
        }
        return render_to_string('widgets/widgets/friends_side_nav.html', context)

class HistoryWidget(Widget):
    user_unique = True
    login_required = True
    
    class Meta():
        verbose_name = 'History Widget'
        verbose_name_plural = 'History Widgets'
    
    def render_content(self, context, *args, **kwargs):
        request = context['request']
        
        activity_events = ActivityEvent.objects.filter(user=request.user).order_by('-timestamp')
    
        # create pager
        page_obj = utils.paging(activity_events, 'page', request, 10)
        object_list = page_obj.object_list

        return render_to_string("widgets/widgets/history.html", {
            "object_list": object_list,
            "page_obj": page_obj,
            "show_avatar": False,
        }, context_instance=RequestContext(request))

class InboxWidget(Widget):
    user_unique = True
    login_required = True
    
    class Meta():
        verbose_name = 'Inbox Widget'
        verbose_name_plural = 'Inbox Widgets'
    
    def render_content(self, context, *args, **kwargs):
        request = context['request']
        user = request.user
        object_list = Message.objects.filter(thread__users=request.user).exclude(sender=user).order_by('-sent_at')
    
        # create pager
        page_obj = utils.paging(object_list, 'page', request, 5)
        object_list = page_obj.object_list
    
        return render_to_string("widgets/widgets/messages.html", {
            'object_list': object_list,
            'view': 'render_listing_inbox',
            'page_obj': page_obj,
        }, context_instance=RequestContext(request))

class MessageWidget(Widget):
    login_required = True
    
    class Meta():
        verbose_name = 'Message Widget'
        verbose_name_plural = 'Message Widgets'
    
    def render_content(self, context, thread_id, *args, **kwargs):
        request = context['request']
        form_class = MessageReplyForm
        qs = Thread.objects.filter(userthread__user=request.user).distinct()
        thread = get_object_or_404(qs, pk=thread_id)
        if request.method == 'POST':
            form = form_class(request.POST, user=request.user, thread=thread)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('messages_inbox'))
        else:
            form = form_class(user=request.user, thread=thread)
            thread.userthread_set.filter(user=request.user).update(unread=False)

        return render_to_string('widgets/widgets/message.html', {
            'thread': thread,
            'form': form
        }, context_instance=RequestContext(request))

class NewsCompetitionsEvents(Widget):
    """
    Renders the latest news, competitions and events.
    Only public content will render.
    """
    class Meta():
        verbose_name = 'News Competitions Events Widget'
        verbose_name_plural = 'News Competitions Events Widgets'
    
    class Panel(object):
        def __init__(self, queryset, rows_per_panel):
            """
            Build panels based on number of objects in queryset and the
            number of rows required per panel. For instance with a rows_per_panel
            of 6 and queryset containing 15 objects, 3 panels will be created
            containing 6, 6 and 3 objects respectively.
            """
            object_list = list(queryset)
            object_list_count = len(object_list)
        
            panels = []
            if object_list_count > 0:
                # generate instance slice offsets from which to populate panels
                slices = range(0, object_list_count, rows_per_panel)
                # populate panels based on instance slices
                for slice_start in slices:
                    panels.append(object_list[slice_start: slice_start + rows_per_panel])

            self.panels = panels
            self.render_controls = (len(panels) > 1)

    @property
    def news_panel(self):
        """
        Returns queryset containing 3 items labeled 'News'.
        """
        news_labels = Label.objects.filter(title__iexact="news")
        queryset = ContentBase.permitted.filter(labels__in=news_labels).order_by("-created")[:18]
        return self.Panel(queryset, 6)

    @property
    def competitions(self):
        """
        Returns queryset containing 3 competitions.
        """
        queryset = Competition.permitted.order_by("-created")[:3]
        return queryset
    
    @property
    def events(self):
        """
        Returns queryset containing 3 upcomming events.
        """
        queryset = []
        entries = Entry.objects.permitted().upcoming().by_content_type(Event).order_by('start')
        if entries:
            for entry in entries:
                content = entry.content
                if content not in queryset:
                    queryset.append(content)

        queryset = queryset[:3]
        return queryset

    def render_content(self, context, *args, **kwargs):
        """
        Renders the widget.
        """
        context = {
            'news_panel': self.news_panel,
            'competitions': self.competitions,
            'events': self.events,
        }
        return render_to_string('widgets/widgets/news_competitions_events.html', context)

class NowPlayingWidget(Widget):
    class Meta():
        verbose_name = 'Now Playing Widget'
        verbose_name_plural = 'Now Playing Widgets'
    
    def get_public_on_air_entry(self, content_type):
        """
        Returns first currently active public entry that has public content
        """
        entries = Entry.objects.permitted().by_content_type(content_type).now().filter(content__is_public=True)
        return entries[0] if entries else None
    
    def get_next_entry(self, content_type):
        valid_entry = None
        now = datetime.now()
        
        entries = Entry.objects.permitted().by_content_type(content_type).filter(start__gt=now).order_by('start')
        for entry in entries:
            if entry.content.is_public:
                valid_entry = entry
                break

        return valid_entry

    def get_public_last_entry(self, content_type):
        """
        Returns last public entry that has public content
        """
        entries = Entry.objects.permitted().by_content_type(content_type).last().filter(content__is_public=True)
        return entries[0] if entries else None
    
    def render_content(self, context, *args, **kwargs):
        # get the current on air show
        show_entry = self.get_public_on_air_entry(Show)
        show = show_entry.content.as_leaf_class() if show_entry else None
       
        # get the primary castmember for the current on air show
        primary_castmembers = show.primary_castmembers if show else None
        primary_castmember = primary_castmembers[0] if primary_castmembers else None
        
        # get the current or last played song and artist info
        song_entry = self.get_public_on_air_entry(Song)
        if not song_entry:
            song_entry = self.get_public_last_entry(Song)
        song = song_entry.content.as_leaf_class() if song_entry else None
        artist = song.get_primary_artist() if song else None
        
        next_entry = self.get_next_entry(Show)
        next_show = next_entry.content.as_leaf_class() if next_entry else None
        next_castmembers = next_show.primary_castmembers if next_show else None
        next_castmember = next_castmembers[0] if next_castmembers else None
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
        return render_to_string('widgets/widgets/now_playing.html', context)

class OnAirWidget(Widget):
    """
    Renders details on the current or upcoming show,
    current song as well as listen live, studio cam and castmember blog links.
    """
    class Meta():
        verbose_name = 'On Air Widget'
        verbose_name_plural = 'On Air Widgets'
    
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
    
    def get_public_last_entry(self, content_type):
        """
        Returns last public entry that has public content
        """
        entries = Entry.objects.permitted().by_content_type(content_type).last().filter(content__is_public=True)
        return entries[0] if entries else None

    def render_content(self, context, *args, **kwargs):
        """
        Renders the widget.
        Returns an empty string if no show is found.
        """
        # get a show to display, either currently on air or coming up next
        on_air = True
        show_entry = self.get_public_on_air_entry(Show)
        if not show_entry:
            show_entry = self.get_public_next_on_air_entry(Show)
            on_air = False
        show = show_entry.content.as_leaf_class() if show_entry else None
      
        if show:
            # get the primary castmember for the current on air show
            primary_castmembers = show.primary_castmembers
            primary_castmember = primary_castmembers[0] if primary_castmembers else None
            
            # build the 'with' string linking to each castmembers blog
            with_str = " & ".join(['<a href="%s">%s</a>' % (castmember.url(), castmember.title) for castmember in primary_castmembers])
        
            # get the current or last played song and artist info
            song_entry = self.get_public_on_air_entry(Song)
            if not song_entry:
                song_entry = self.get_public_last_entry(Song)
            song = song_entry.content.as_leaf_class() if song_entry else None
            artist = song.get_primary_artist() if song else None

            context.update({
                'entry': show_entry,
                'show': show,
                'on_air': on_air,
                'with_str': with_str,
                'primary_castmember': primary_castmember,
                'song': song,
                'artist': artist,
            })
            return render_to_string('widgets/widgets/on_air.html', context)
        else:
            return ''

class PasswordResetWidget(Widget):
    receive_post = True
    
    class Meta():
        verbose_name = 'Password Reset Widget'
        verbose_name_plural = 'Password Reset Widgets'
    
    def render_content(self, context, *args, **kwargs):
        kwargs.update({
            'template_name': 'widgets/widgets/password_reset.html',
            'post_reset_redirect': reverse('password_reset_complete'),
        })
        response = password_reset_confirm(context['request'], *args, **kwargs)
        if isinstance(response, HttpResponseRedirect):
            return response
        else:
            return response.content

class PasswordResetCompleteWidget(Widget):
    class Meta():
        verbose_name = 'Password Reset Complete Widget'
        verbose_name_plural = 'Password Reset Complete Widgets'
    
    def render_content(self, context, *args, **kwargs):
        return render_to_string("widgets/widgets/password_reset_complete.html", context)

class ReviewsListingWidget(Widget):
    class Meta():
        verbose_name = 'Reviews Listing Widget'
        verbose_name_plural = 'Reviews Listing Widgets'
    
    def render_content(self, context, *args, **kwargs):
        request = context['request']
        
        reviews_label = Label.objects.get(title__iexact='reviews')
        queryset=Post.permitted.filter(labels=reviews_label).order_by('-created')
        header = utils.ReviewsHeader(request, reviews_label)
        queryset_modifiers = [header.page_menu.queryset_modifier,]
        for queryset_modifier in queryset_modifiers:
            queryset = queryset_modifier.updateQuery(queryset)

    
        return list_detail.object_list(
            request=request,
            queryset=queryset,
            template_name='widgets/widgets/listing_wide.html',
            paginate_by=10,
            extra_context={
                'header': header,
            },
        ).content

class SentWidget(Widget):
    user_unique = True
    login_required = True
    
    class Meta():
        verbose_name = 'Sent Widget'
        verbose_name_plural = 'Sent Widgets'
    
    def render_content(self, context, *args, **kwargs):
        request = context['request']
        user = request.user
        object_list = Message.objects.filter(sender=user).order_by('-sent_at')
    
        # create pager
        page_obj = utils.paging(object_list, 'page', request, 5)
        object_list = page_obj.object_list
    
        return render_to_string("widgets/widgets/messages.html", {
            'object_list': object_list,
            'view': 'render_listing_inbox',
            'page_obj': page_obj,
        }, context_instance=RequestContext(request))

class ShowsListingWidget(Widget):
    class Meta():
        verbose_name = 'Shows Listing Widget'
        verbose_name_plural = 'Shows Listing Widgets'
    
    def render_content(self, context, *args, **kwargs):
        request = context['request']
        
        queryset = Entry.objects.permitted().by_content_type(Show).week().order_by('start')
        header = utils.ShowsHeader(request)
        queryset_modifiers = [header.page_menu.queryset_modifier,]
        for queryset_modifier in queryset_modifiers:
            queryset = queryset_modifier.updateQuery(queryset)

        return list_detail.object_list(
            request=request,
            queryset=queryset,
            template_name='widgets/widgets/listing_block.html',
            extra_context={
                'header': header,
            },
        ).content

class SlidingPromoWidget(Widget):
    class Meta():
        verbose_name = 'Sliding Promo Widget'
        verbose_name_plural = 'Sliding Promo Widgets'
    
    def render_content(self, context, *args, **kwargs):
        """
        Renders the sliding promotions widget. 
        Only public content will render.
        Returns an empty string if no suitable content is found to render.
        """
        # only public slots containing public content qualify as valid items
        slots =  self.slidingpromowidgetslot_set.permitted()
        if slots:
            items = []
            for slot in slots:
                content = slot.content
                if content.is_public:
                    content = content.as_leaf_class()
                    # grab item url from view method or property
                    try:
                        url = content.url(context)
                    except TypeError:
                        url = content.url
                    items.append({
                        'title': slot.title,
                        'content': content,
                        'url': url,
                    })

            if items: 
                context = {
                    'items': items
                }
                return render_to_string('widgets/widgets/promotions.html', context)
        return ''

class SlidingPromoWidgetSlot(ModelBase):
    title = models.CharField(max_length=255)
    widget = models.ForeignKey(SlidingPromoWidget)
    content = models.ForeignKey(
        ContentBase,
        limit_choices_to = ~Q(classname__in=['PromoWidget', 'PromoWidgetSlot', 'ModelBase', 'ContentBase',]) & Q(is_public=True),
        related_name="promo_content",
    )
    class Meta:
        verbose_name = 'Sliding Promo Widget Slot'
        verbose_name_plural = 'Sliding Promo Widget Slots'

class StatusUpdates(Widget):
    """
    Renders status updates for DJ's and Friends.
    """
    user_unique = True
    
    class Meta():
        verbose_name = 'Status Updates Widget'
        verbose_name_plural = 'Status Updates Widgets'
    
    def get_castmember_updates(self):
        """
        Gets 4 primary castmember status updates sorted by timestamp descending.
        Primary castmembers are determined by credits with role 1.
        """
        credits = Credit.objects.filter(role='1', show__in=Show.permitted.all).select_related('castmember')
        castmember_owners = [credit.castmember.owner for credit in credits]
        return StatusUpdate.objects.filter(user__in=castmember_owners).select_related('user').order_by('-timestamp')[:4]

    def get_friends_updates(self, user):
        """
        Gets 4 user's friend's status updates sorted by timestamp descending.
        """
        friends_status_updates = []
        if user.is_authenticated():
            friends = Friendship.objects.friends_for_user(user)
            friends = [friend['friend'] for friend in friends]
            friends_status_updates = StatusUpdate.objects.filter(user__in=friends).select_related('user').order_by('-timestamp')[:4]

        return friends_status_updates
        
    def render_content(self, context, *args, **kwargs):
        """
        Renders the widget.
        """
        request = context['request']
        user = request.user
      
        context.update({
            'widget': self,
            'castmember_updates': self.get_castmember_updates(),
            'friends_updates': self.get_friends_updates(user),
        })
        return render_to_string('widgets/widgets/status_updates.html', context)

class YourFriends(Widget):
    """
    Renders friends listing for currently logged in user.
    If anonymous renders link to find friends page.
    """
    user_unique = True
    
    class Meta():
        verbose_name = 'Your Friends Widget'
        verbose_name_plural = 'Your Friends Widgets'
    
    def render_content(self, context, *args, **kwargs):
        """
        Renders the widget.
        """
        request = context['request']
        user = request.user
        context.update({
            'widget': self,
        })
       
        if user.is_authenticated():
            friends = Friendship.objects.friends_for_user(user)
            friends_count = len(friends)

            try:
                friends = random.sample(friends, 10)
            except ValueError:
                pass
                
            friends = [friend['friend'] for friend in friends]
    
            context.update({
                'friends': friends,
                'friends_count': friends_count
            })
        return render_to_string('widgets/widgets/your_friends.html', context)

class Layout(ModelBase):
    view_name = models.CharField(max_length=128, choices=VIEW_CHOICES)

class LayoutTopLeftRight(Layout):
    top_widgets = models.ManyToManyField(
        Widget, 
        related_name="top_widgets",
        through="LayoutTopLeftRightTopSlot",
    )
    left_widgets = models.ManyToManyField(
        Widget, 
        related_name="left_widgets",
        through="LayoutTopLeftRightTopLeftSlot",
    )
    right_widgets = models.ManyToManyField(
        Widget, 
        related_name="right_widgets",
        through="LayoutTopLeftRightTopRightSlot",
    )
    background = models.BooleanField()

    class Meta():
        verbose_name = 'Top Left Right Layout'
        verbose_name_plural = 'Top Left Right Layouts'

    def __unicode__(self):
        for choice in VIEW_CHOICES:
            if self.view_name == choice[0]:
                return "%s - %s" % (choice[1], self._meta.verbose_name)
        
        return "%s for Unkown View" % self._meta.verbose_name

    def render(self, request, *args, **kwargs):
        context = RequestContext(request)
        
        #build top widgets
        top_widgets = self.top_widgets.permitted().order_by('top_widgets_slots__position')
        top_widgets = [widget.render(context, *args, **kwargs) for widget in top_widgets]
        #build left widgets
        left_widgets = self.left_widgets.permitted().order_by('left_widgets_slots__position')
        left_widgets = [widget.render(context, *args, **kwargs) for widget in left_widgets]
        #build right widgets
        right_widgets = self.right_widgets.permitted().order_by('right_widgets_slots__position')
        right_widgets = [widget.render(context, *args, **kwargs) for widget in right_widgets]

        #widgets returning a redirect should cause the page to redirect
        for widget in top_widgets + left_widgets + right_widgets:
            if isinstance(widget, HttpResponseRedirect):
                return widget
        
        return render_to_response(
            'widgets/layout/top_left_right.html', 
            {  
                'layout': self,
                'top_widgets': top_widgets,
                'left_widgets': left_widgets,
                'right_widgets': right_widgets,
            }, 
            context_instance=RequestContext(request)
        )

class Slot(models.Model):
    position = models.IntegerField()

    class Meta:
        abstract = True
        ordering = ('position',)

    def __unicode__(self):
        return "%s slot for %s" % (self.widget, self.layout)

def isthroughwidgetfield(thing):
    """
    Determines if a field relates to the Widget model and if it has a through option set
    """
    from django.db.models.fields.related import ReverseManyRelatedObjectsDescriptor
    try:
        if thing.__class__ == ReverseManyRelatedObjectsDescriptor:
            if Widget in thing.field.rel.to.__mro__:
                return thing.field.rel.through
    except AttributeError:
        return False
    return False

# dynamically create 'through' classes and register for admin
clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
for clsmember in clsmembers:
    cls = clsmember[1]
    if Layout in cls.__mro__ and cls != Layout:
        widget_through_fields = inspect.getmembers(cls, isthroughwidgetfield)
        inlines = []
        for widget_through_field in widget_through_fields:
            name = widget_through_field[0]
            field = widget_through_field[1].field
            through = field.rel.through
            new_model = type(
                through,
                (Slot,), 
                {
                    '__module__': __name__,
                    'widget': models.ForeignKey(Widget, related_name='%s_slots' % name),
                    'layout': models.ForeignKey(cls, related_name='%s_slots' % name),
                }
            )
            inlines.append(type(
                "%sInline" % through,
                (admin.TabularInline,),
                {
                    'model': new_model,
                    'verbose_name': name.replace("_", " ").title(),
                    'verbose_name_plural': '%s' % name.replace("_", " ").title(),
                },
            ))
        cls_admin = type(
            "%sAdmin" % cls.__name__,
            (admin.ModelAdmin,),
            {'inlines': inlines},
        )
        admin.site.register(cls, cls_admin)

# For some reason importing urlpatterns causes admin not 
# to register our models. Import admin again to force register.
import admin
