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
