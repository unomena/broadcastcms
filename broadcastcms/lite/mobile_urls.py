import datetime

from django.conf import settings
from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_list

from broadcastcms.calendar.models import Entry
from broadcastcms.competition.models import Competition
from broadcastcms.event.models import Event
from broadcastcms.gallery.models import Gallery
from broadcastcms.post.models import Post
from mobile_views import *
from voting.views import xmlhttprequest_vote_on_object


# Custom direct to template
def direct_to_template(request, template):
    context = RequestContext(request, {})
    return render_to_response(template, context)
    
# Required querysets
competition_list_params = {
    'queryset' : Competition.permitted.all(),
    'allow_empty': True,
    'paginate_by': 5,
    'template_name': 'mobile/content/competitions/competitions.html',
}
event_list_params = {
    'queryset' : Entry.objects.permitted().by_content_type(Event).order_by('start').filter(start__gte=datetime.datetime.now()),
    'allow_empty': True,
    'paginate_by': 5,
    'template_name': 'mobile/content/events/events.html',
}
gallery_list_params = {
    'queryset' : Gallery.permitted.all(),
    'allow_empty': True,
    'paginate_by': 5,
    'template_name': 'mobile/content/galleries/galleries.html',
}
news_list_params = {
    'queryset' : Post.permitted.all(),
    'allow_empty': True,
    'paginate_by': 5,
    'template_name': 'mobile/content/news/news.html',
}



# Url patterns
urlpatterns = patterns('',
    
    # Accounts
    (r'account/sign-in/$', account_login),
    (r'account/sign-out/$', account_logout),
    (r'account/sign-up/(?P<result>[\w-]+)/$', account_confirm),
    (r'account/sign-up/$', account_register),
    (r'account/profile/$', account_profile),
    
    # Comment
    (r'comment-add/$', comment_add),
    (r'comment/(?P<slug>[\w-]+)/$', custom_object_detail, {'comment_add': True}),
    (r'comment/(?P<slug>[\w-]+)/(?P<result>[\w-]+)/$', custom_object_detail, {'comment_add': True}),
    
    # Competition
    (r'competition/$', object_list, competition_list_params),
    (r'competition/rules/$', direct_to_template, {'template':'mobile/content/competitions/competition-rules.html'}),
    (r'competition/(?P<page>[0-9]+)/$', object_list, competition_list_params),
    (r'competition/(?P<slug>[\w-]+)/$', custom_object_detail, {'classname': 'Competition'}),
    
    # Event
    (r'event/$', object_list, event_list_params),
    (r'event/(?P<page>[0-9]+)/$', object_list, event_list_params),
    (r'event/(?P<slug>[\w-]+)/$', custom_object_detail, {'classname': 'Event'}),
    
    # Gallery
    (r'gallery/$', object_list, gallery_list_params),
    (r'gallery/(?P<page>[0-9]+)/$', object_list, gallery_list_params),
    (r'gallery/(?P<slug>[\w-]+)/$', custom_object_detail, {'classname': 'Gallery'}),
    
    # News
    (r'news/$', object_list, news_list_params),
    (r'news/(?P<page>[0-9]+)/$', object_list, news_list_params),
    (r'news/(?P<slug>[\w-]+)/$', custom_object_detail, {'classname': 'Post'}),
    
    # Shows and DJ pages
    #(r'show/(?P<dj_slug>[\w-]+)/(?P<slug>[\w-]+)/$', content_details, {'mode':'djcontent'}),
    (r'show/$', shows_line_up),
    (r'show/(?P<dj_slug>[\w-]+)/$', shows_dj_blog),
    (r'show/line-up/(?P<weekday>[\w-]+)/$', shows_line_up),
    (r'show/(?P<dj_slug>[\w-]+)/(?P<slug>[\w-]+)/$', custom_object_detail),
    (r'show/(?P<dj_slug>[\w-]+)/(?P<slug>[\w-]+)/comment/$', custom_object_detail, {'comment_add': True}),
    
    # Contact
    (r'contact/(?P<dj_slug>[\w-]+)/$', contact),
    (r'contact/$', contact),
    
    # Foooter links
    (r'privacy/$', direct_to_template, {'template':'mobile/content/footer/privacy.html'}),
    (r'terms/$', direct_to_template, {'template':'mobile/content/footer/terms.html'}),
    
    # Static urls
    (r'^$', direct_to_template, {'template':'mobile/content/home.html'}),
    (r'news/$', direct_to_template, {'template':'mobile/content/news/news.html'}),
    (r'about/$', direct_to_template, {'template':'mobile/content/about.html'}),
    (r'contact/$', direct_to_template, {'template':'mobile/content/contact.html'}),
    
    # Voting / Likes
    (r'voting/(?P<slug>[\w-]+)/$', vote_on_object, {'model': ContentBase, 'slug_field': 'slug', 'direction': 'up'}),
)


if settings.SERVE_STATIC:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
