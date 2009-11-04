from django.conf.urls.defaults import *


urlpatterns = patterns("broadcastcms.status.views",
    url(r"^update/$", "update", name="status_update"),
)
