from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from broadcastcms.base.models import ContentBase
from broadcastcms.calendar.models import Entry
from broadcastcms.show.models import Show, CastMember
from broadcastcms.radio.models import Song

register = template.Library()

@register.tag
def on_air(parser, token):
    return OnAirNode()

class OnAirNode(template.Node):
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

    def get_primary_castmember(self, show):
        """
        Returns the primary public castmember for the given show.
        Primary castmember is determined by credit roles.
        """
        credits = show.credits.all().filter(castmember__is_public=True).order_by('role')
        return credits[0].castmember if credits else None

    def get_castmembers(self, show):
        """
        Returns all public castmembers for the given show.
        """
        credits = show.credits.filter(castmember__is_public=True, role=1)
        return credits if credits else None
    
    def render(self, context):
        """
        Renders the homepage On Air box containing details on the
        current show and current song as well as listen live, studio
        cam and castmember blog links
        """
        # get a show to display, either currently on air or coming up
        on_air = True
        show_entry = self.get_public_on_air_entry(Show)
        if not show_entry:
            show_entry = self.get_public_next_on_air_entry(Show)
            on_air = False
        show = show_entry.content.as_leaf_class() if show_entry else None
       
        # get the primary castmember for the current on air show
        primary_castmember = self.get_primary_castmember(show) if show else None

        # get all cast members for the current show
        all_castmembers = self.get_castmembers(show) if show else None
        
        # get the current playing song and artist info
        song_entry = self.get_public_on_air_entry(Song)
        song = song_entry.content.as_leaf_class() if song_entry else None
        artist = song.credits.filter(artist__is_public=True).order_by('role') if song else None
        artist = artist[0].artist if artist else None

        context.update({
            'entry': show_entry,
            'show': show,
            'on_air': on_air,
            'primary_castmember': primary_castmember,
            'all_castmembers': all_castmembers,
            'song': song,
            'artist': artist,
        })
        return render_to_string('mobile/inclusion_tags/home/on_air.html', context)
        
        
class EntryUpdatesNode(template.Node):
    def __init__(self, count=5):
        self.count = count
        super(EntryUpdatesNode, self).__init__()

    def get_instances(self, settings):
        """
        Returns public instance for those types specified in the Settings object's
        update_types field, sorted on created date descending. The number of items returned
        is limited to the value of self.count.
        """
        # get the update types from settings
        update_types = [update_type.model_class().__name__ for update_type in settings.update_types.all()]

        # collect public instances, limited to count, sorted on created descending
        instances = ContentBase.permitted.filter(classname__in=update_types).order_by("-created")[:self.count]
        
        # return list of instance leaves
        return [instance.as_leaf_class() for instance in instances]

    def render(self, context):
        """
        Renders the latest update entries as filterd by cast member or type.
        """
        instances = self.get_instances(context['settings'])
        context.update({
            'instances': instances,
        })
        return render_to_string('mobile/inclusion_tags/misc/updates.html', context)

@register.tag
def homepage_updates(parser, token):
    return EntryUpdatesNode(count=5)


class UpdateClassnameNode(template.Node):
    def __init__(self, obj_name):
        self.obj_name = obj_name

    def render(self, context):
        obj = context[self.obj_name]
        classname = obj.classname
        if obj.owner:
            castmembers = CastMember.permitted.filter(owner=obj.owner)
            if castmembers:
                return castmembers[0].title
        if classname == 'Post':
            return 'News'
        return classname
    
@register.tag
def get_classname(parser, token):
    try:
        tag_name, obj_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s requires exactly one argument" % token.contents
    
    return UpdateClassnameNode(obj_name)


