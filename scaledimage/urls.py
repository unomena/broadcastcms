from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    # Static media backup url
    # TODO: Add a check to disable dev server media serving on production, i.e. when not in debug mode.
    url(r'^media/content_images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT + 'content_images'}),
)
