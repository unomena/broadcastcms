from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from friends.models import Friendship

from broadcastcms.base.models import ContentBase
from broadcastcms.cache.decorators import cache_view_function
from broadcastcms.calendar.models import Entry
from broadcastcms.competition.models import Competition
from broadcastcms.event.models import Event
from broadcastcms.label.models import Label
from broadcastcms.radio.models import Song
from broadcastcms.show.models import Credit, Show
from broadcastcms.status.models import StatusUpdate

#class SSIContentResolver(object):
#    """
#    Renders either an SSI tag or normal render based on debug mode.
#    """
#    def render(self, context):
#        """
#        Returns either self.render_ssi or self.render_content based on debug mode.
#        self.render_content to be implimented by subclasses.
#        """
#        if settings.DEBUG:
#            return self.render_content(context)
#        else:
#            return self.render_ssi()
#
#    def render_ssi(self):
#        """
#        Renders SSI tag. URL is determined through self.get_absolute_url()
#        which subclasses have to impliment
#        """
#        return '<!--# include virtual="%s" -->' % self.get_absolute_url()


#class Advert(object):
#    """
#    Renders advert based on current section and advert specified for
#    that section in settings. Only public banners are rendered.
#    """
#    @cache_view_function(10*60, respect_path=True)
#    def render(self, context):
#        """
#        Render the widget.
#        """
#        section = context['section']
#        settings = context['settings']
#        banners = settings.get_section_banners(section)
#        return banners[0].render() if banners else ""

#class NewsCompetitionsEvents(object):
#    """
#    Renders the latest news, competitions and events.
#    Only public content will render.
#    """
#    class Panel(object):
#        def __init__(self, queryset, rows_per_panel):
#            """
#            Build panels based on number of objects in queryset and the
#            number of rows required per panel. For instance with a rows_per_panel
#            of 6 and queryset containing 15 objects, 3 panels will be created
#            containing 6, 6 and 3 objects respectively.
#            """
#            object_list = list(queryset)
#            object_list_count = len(object_list)
#        
#            panels = []
#            if object_list_count > 0:
#                # generate instance slice offsets from which to populate panels
#                slices = range(0, object_list_count, rows_per_panel)
#                # populate panels based on instance slices
#                for slice_start in slices:
#                    panels.append(object_list[slice_start: slice_start + rows_per_panel])
#
#            self.panels = panels
#            self.render_controls = (len(panels) > 1)
#
#    @property
#    def news_panel(self):
#        """
#        Returns queryset containing 3 items labeled 'News'.
#        """
#        news_labels = Label.objects.filter(title__iexact="news")
#        queryset = ContentBase.permitted.filter(labels__in=news_labels).order_by("-created")[:18]
#        return self.Panel(queryset, 6)
#
#    @property
#    def competitions(self):
#        """
#        Returns queryset containing 3 competitions.
#        """
#        queryset = Competition.permitted.order_by("-created")[:3]
#        return queryset
#    
#    @property
#    def events(self):
#        """
#        Returns queryset containing 3 upcomming events.
#        """
#        queryset = []
#        entries = Entry.objects.permitted().upcoming().by_content_type(Event).order_by('start')
#        if entries:
#            for entry in entries:
#                content = entry.content
#                if content not in queryset:
#                    queryset.append(content)
#
#        queryset = queryset[:3]
#        return queryset
#
#    @cache_view_function(10*60)
#    def render(self, context):
#        """
#        Renders the widget.
#        """
#        context = {
#            'news_panel': self.news_panel,
#            'competitions': self.competitions,
#            'events': self.events,
#        }
#        return render_to_string('news_competitions_events.html', context)
#
#class StatusUpdates(SSIContentResolver):
#    """
#    Renders status updates for DJ's and Friends.
#    """
#    def get_absolute_url(self):
#        return reverse('session_status_updates')
#
#    def get_castmember_updates(self):
#        """
#        Gets 4 primary castmember status updates sorted by timestamp descending.
#        Primary castmembers are determined by credits with role 1.
#        """
#        credits = Credit.objects.filter(role='1', show__in=Show.permitted.all).select_related('castmember')
#        castmember_owners = [credit.castmember.owner for credit in credits]
#        return StatusUpdate.objects.filter(user__in=castmember_owners).select_related('user').order_by('-timestamp')[:4]
#
#    def get_friends_updates(self, user):
#        """
#        Gets 4 user's friend's status updates sorted by timestamp descending.
#        """
#        friends_status_updates = []
#        if user.is_authenticated():
#            friends = Friendship.objects.friends_for_user(user)
#            friends = [friend['friend'] for friend in friends]
#            friends_status_updates = StatusUpdate.objects.filter(user__in=friends).select_related('user').order_by('-timestamp')[:4]
#
#        return friends_status_updates
#        
#    @cache_view_function(5*60, respect_user=True)
#    def render_content(self, context):
#        """
#        Renders the widget.
#        """
#        request = context['request']
#        user = request.user
#      
#        context.update({
#            'castmember_updates': self.get_castmember_updates(),
#            'friends_updates': self.get_friends_updates(user),
#        })
#        return render_to_string('status_updates.html', context)
#
#class YourFriends(SSIContentResolver):
#    """
#    Renders friends listing for currently logged in user.
#    If anonymous renders link to find friends page.
#    """
#    def get_absolute_url(self):
#        return reverse('session_your_friends')
#
#    @cache_view_function(10*60, respect_user=True)
#    def render_content(self, context):
#        """
#        Renders the widget.
#        """
#        request = context['request']
#        user = request.user
#       
#        if user.is_authenticated():
#            friends = Friendship.objects.friends_for_user(user)
#            friends_count = len(friends)
#            friends = [friend['friend'] for friend in friends][:10]
#    
#            context.update({
#                'friends': friends,
#                'friends_count': friends_count
#            })
#        return render_to_string('your_friends.html', context)
