from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('',
   url(r'^media/richtext/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT + 'richtext'}, name='media'),
)
