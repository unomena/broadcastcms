from os import path

from django.conf.urls.defaults import *
from django.conf import settings


SCRIPT_PATH =  path.abspath(path.dirname(__file__))


urlpatterns = patterns('',
   url(r'^media/richtext/(?P<path>.*)$', 'django.views.static.serve', {'document_root':SCRIPT_PATH + '/media'}, name='media'),
)
