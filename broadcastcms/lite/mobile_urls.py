from django.conf import settings
from django.conf.urls.defaults import *

from mobile_views import *

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
)

if settings.SERVE_STATIC:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
