from django.conf import settings
from django.conf.urls.defaults import *

import production_urls

if settings.DEBUG:
    urlpatterns = production_urls.urlpatterns + patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
