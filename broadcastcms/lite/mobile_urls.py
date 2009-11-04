from django.conf import settings
from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.template import RequestContext

# Custom direct to template
def direct_to_template(request, template, name=None):
    context = RequestContext(request, {})
    return render_to_response(template, context)


# Url patterns
urlpatterns = patterns('',
    (r'^$', direct_to_template, {'template':'mobile/content/home.html'}),
    (r'shows/$', direct_to_template, {'template':'mobile/content/shows.html'}),
    (r'news/$', direct_to_template, {'template':'mobile/content/news.html'}),
    (r'events/$', direct_to_template, {'template':'mobile/content/events.html'}),
    (r'competions/$', direct_to_template, {'template':'mobile/content/comps.html'}),
    (r'galleries/$', direct_to_template, {'template':'mobile/content/galleries.html'}),
    (r'about/$', direct_to_template, {'template':'mobile/content/about.html'}),
    (r'contact/$', direct_to_template, {'template':'mobile/content/contact.html'}),
    (r'sign-in/$', direct_to_template, {'template':'mobile/content/sign-in.html'}),
)


if settings.SERVE_STATIC:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
