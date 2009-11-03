from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns("broadcastcms.status.views",
    url(r"^update/$", "update", name="status_update"),
)
