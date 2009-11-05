from django.conf import settings
from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.template import RequestContext

from mobile_views import *


# Custom direct to template
def direct_to_template(request, template):
    context = RequestContext(request, {})
    return render_to_response(template, context)


# Url patterns
urlpatterns = patterns('',
    # Competition
    (r'competitions/$', direct_to_template, {'template':'mobile/content/competitions/competitions.html'}),
    #(r'competions/rules/$', direct_to_template, {'template':'mobile/content/comps.html'}),
    #(r'competitions/(?P<slug>[\w-]+)/$', content_details, {'mode':'general'}),
    
    # Shows and DJ pages
    #(r'shows/lineup/(?P<weekday>[\w-]+)/$', shows),
    #(r'shows/(?P<dj_slug>[\w-]+)/(?P<slug>[\w-]+)/$', content_details, {'mode':'djcontent'}),
    #(r'shows/(?P<dj_slug>[\w-]+)/$', dj_page, {'template':'mobile/content/shows/shows.html'}),
    (r'shows/$', shows),
    
    
    # Static urls
    (r'^$', direct_to_template, {'template':'mobile/content/home.html'}),
    (r'news/$', direct_to_template, {'template':'mobile/content/news/news.html'}),
    (r'events/$', direct_to_template, {'template':'mobile/content/events/events.html'}),
    (r'galleries/$', direct_to_template, {'template':'mobile/content/galleries/galleries.html'}),
    (r'about/$', direct_to_template, {'template':'mobile/content/about.html'}),
    (r'contact/$', direct_to_template, {'template':'mobile/content/contact.html'}),
    (r'sign-in/$', direct_to_template, {'template':'mobile/content/members/sign-in.html'}),
)


if settings.SERVE_STATIC:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
