from django.conf.urls.defaults import *


urlpatterns = patterns("broadcastcms.history.views",
    url(r"^$", "my_history", name="account_history"),
)
