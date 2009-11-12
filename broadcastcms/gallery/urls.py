from django.conf.urls.defaults import *

from views import *


urlpatterns = patterns('',
    # feeds
    url(r'(?P<slug>[\w-]+).xml$', gallery_xml, name='gallery_xml'),
)
