from datetime import datetime
import inspect, sys

from django.contrib import admin
from django.db import models
from django.db.models.query import Q
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.template import RequestContext

from broadcastcms.base.models import ModelBase, ContentBase
from broadcastcms.calendar.models import Entry
from broadcastcms.lite.desktop_urls import urlpatterns
from broadcastcms.radio.models import Song
from broadcastcms.show.models import Show

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
        
    def get_ssi_url(self):
        return reverse("ssi", kwargs={'slug': self.slug})

class AccountMenuWidget(Widget):
    class Meta():
        verbose_name = 'Account Menu Widget'
        verbose_name_plural = 'Account Menu Widgets'
   
    def render_content(self, context):
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
        account_section = request.path.split('/')[2]
       
        profile = request.user.profile

        context.update({
            'menu_items': menu_items,
            'account_section': account_section,
            'profile': profile,
        })
        return render_to_string('widgets/widgets/account_menu.html', context)

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

    def render_content(self, context):
        context = {
            'widget': self,
            'content': self.content.as_leaf_class(),
        }
        return render_to_string('widgets/widgets/banner.html', context)

class FriendsWidget(Widget):
    class Meta():
        verbose_name = 'Friends Widget'
        verbose_name_plural = 'Friends Widgets'
    
    def render_content(self, context):
        from friends.models import Friendship
        from broadcastcms.lite import utils

        request = context['request']

        friends = Friendship.objects.friends_for_user(request.user)
    
        # create pager
        page_obj = utils.paging([friend['friend'] for friend in friends], 'page', request, 5)
        friends = page_obj.object_list

        context = {
            'friends': friends,
            'page_obj': page_obj,
            'request': request,
        }
        return render_to_string('widgets/widgets/friends.html', context)

class FriendsSideNavWidget(Widget):
    class Meta():
        verbose_name = 'Friends Side Navigation Widget'
        verbose_name_plural = 'Friends Side Navigation Widgets'
    
    def render_content(self, context):
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

    def render_content(self, context):
        # get the current on air show
        show_entry = self.get_public_on_air_entry(Show)
        show = show_entry.content.as_leaf_class() if show_entry else None
       
        # get the primary castmember for the current on air show
        primary_castmembers = show.primary_castmembers if show else None
        primary_castmember = primary_castmembers[0] if primary_castmembers else None
        
        # get the current playing song and artist info
        song_entry = self.get_public_on_air_entry(Song)
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

    def render_content(self, context):
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
        
            # get the current playing song and artist info
            song_entry = self.get_public_on_air_entry(Song)
            song = song_entry.content.as_leaf_class() if song_entry else None
            artist = song.credits.all().filter(artist__is_public=True).order_by('role') if song else None

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

class SlidingPromoWidget(Widget):
    class Meta():
        verbose_name = 'Sliding Promo Widget'
        verbose_name_plural = 'Sliding Promo Widgets'
    
    def render_content(self, context):
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

    def render(self, request):
        return render_to_response(
            'widgets/layout/top_left_right.html', 
            {  
                'layout': self,
                'top_widgets': self.top_widgets.permitted().order_by('top_widgets_slots__position'),
                'left_widgets': self.left_widgets.permitted().order_by('left_widgets_slots__position'),
                'right_widgets': self.right_widgets.permitted().order_by('right_widgets_slots__position'),
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
