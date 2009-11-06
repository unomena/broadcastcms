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
    (r'competition/$', direct_to_template, {'template':'mobile/content/competitions/competitions.html'}),
    #(r'competions/rules/$', direct_to_template, {'template':'mobile/content/comps.html'}),
    #(r'competitions/(?P<slug>[\w-]+)/$', content_details, {'mode':'general'}),
    
    # Shows and DJ pages
    (r'show/lineup/(?P<weekday>[\w-]+)/$', shows_line_up),
    #(r'show/(?P<dj_slug>[\w-]+)/(?P<slug>[\w-]+)/$', content_details, {'mode':'djcontent'}),
    (r'show/(?P<dj_slug>[\w-]+)/$', shows_dj_blog),
    (r'show/$', shows_line_up),
    
    # Accounts
    (r'account/sign-in/$', account_login),
    (r'account/sign-out/$', account_logout),
    
    # Foooter links
    (r'privacy/$', direct_to_template, {'template':'mobile/content/footer/privacy.html'}),
    (r'terms/$', direct_to_template, {'template':'mobile/content/footer/terms.html'}),
    
    # Static urls
    (r'^$', direct_to_template, {'template':'mobile/content/home.html'}),
    (r'news/$', direct_to_template, {'template':'mobile/content/news/news.html'}),
    (r'event/$', direct_to_template, {'template':'mobile/content/events/events.html'}),
    (r'gallery/$', direct_to_template, {'template':'mobile/content/galleries/galleries.html'}),
    (r'about/$', direct_to_template, {'template':'mobile/content/about.html'}),
    (r'contact/$', direct_to_template, {'template':'mobile/content/contact.html'}),
)


if settings.SERVE_STATIC:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
